/**
 * Cloudflare Pages Function — API 代理
 * 将 /api/v1/* 请求转发到 Vercel Serverless 后端
 */

const API_BASE = env => env.API_BASE_URL || 'https://starcraft-team-data-platform.vercel.app';

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const backendUrl = `${API_BASE(env)}${url.pathname}${url.search}`;

  // 复制并清理 headers（移除 forbidden headers）
  const newHeaders = new Headers();
  for (const [key, value] of request.headers.entries()) {
    // 跳过 Cloudflare 禁止转发的 header
    if (key.toLowerCase() !== 'host') {
      newHeaders.append(key, value);
    }
  }
  // 确保 Content-Type 存在
  if (!newHeaders.has('Content-Type')) {
    newHeaders.set('Content-Type', 'application/json');
  }
  newHeaders.set('Accept', 'application/json');

  try {
    // 处理请求体
    let body = null;
    if (request.method !== 'GET' && request.method !== 'HEAD' && request.method !== 'OPTIONS') {
      // 读取请求体并转为文本（避免 ReadableStream 传递问题）
      try {
        const text = await request.text();
        if (text) {
          body = text;
        }
      } catch (e) {
        // 无法读取 body，不传递
      }
    }

    const backendRequest = new Request(backendUrl, {
      method: request.method,
      headers: newHeaders,
      body: body,
    });

    const response = await fetch(backendRequest, {
      cf: {
        // 禁用 Cloudflare 的缓存
        cacheTtl: 0,
        cacheEverything: false,
      },
    });

    // 复制响应
    const responseHeaders = new Headers(response.headers);
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    responseHeaders.delete('Content-Security-Policy');
    responseHeaders.delete('content-security-policy');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'Backend unavailable',
        detail: error.message || String(error),
        url: backendUrl,
      }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      },
    );
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
