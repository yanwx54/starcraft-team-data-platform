/**
 * Cloudflare Pages Function — API 代理
 * 将 /api/v1/* 请求转发到 Vercel Serverless 后端，解决国内访问问题。
 *
 * 环境变量（在 Cloudflare Dashboard 中配置）:
 *   API_BASE_URL = https://your-project.vercel.app
 */

const API_BASE = env => env.API_BASE_URL || 'https://starcraft-team-data-platform.vercel.app';

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  // 构建后端 URL
  const backendUrl = `${API_BASE(env)}${url.pathname}${url.search}`;

  // 转发请求
  const backendRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body,
  });

  try {
    const response = await fetch(backendRequest);

    // 复制响应并添加 CORS 头
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });

    newResponse.headers.set('Access-Control-Allow-Origin', '*');
    newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    return newResponse;
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Backend unavailable' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
