import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/HomeView.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'matches',
        name: 'MatchList',
        component: () => import('../views/MatchListView.vue'),
        meta: { title: '比赛列表' },
      },
      {
        path: 'matches/:id',
        name: 'MatchDetail',
        component: () => import('../views/MatchDetailView.vue'),
        meta: { title: '比赛详情' },
      },
      {
        path: 'players',
        name: 'PlayerList',
        component: () => import('../views/PlayerListView.vue'),
        meta: { title: '选手列表' },
      },
      {
        path: 'players/:id',
        name: 'PlayerDetail',
        component: () => import('../views/PlayerDetailView.vue'),
        meta: { title: '选手详情' },
      },
      {
        path: 'vs',
        name: 'VsQuery',
        component: () => import('../views/VsQueryView.vue'),
        meta: { title: '对战查询' },
      },
      {
        path: 'players/:id/vs/:opponentId',
        name: 'PlayerVs',
        component: () => import('../views/PlayerVsView.vue'),
        meta: { title: '选手对阵' },
      },
      {
        path: 'maps',
        name: 'Maps',
        component: () => import('../views/MapView.vue'),
        meta: { title: '地图' },
      },
      {
        path: 'maps/:id',
        name: 'MapDetail',
        component: () => import('../views/MapDetailView.vue'),
        meta: { title: '地图详情' },
      },
      {
        path: 'rankings',
        name: 'Rankings',
        component: () => import('../views/RankingView.vue'),
        meta: { title: '排行榜' },
      },
    ],
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/AdminLoginView.vue'),
    meta: { title: '管理员登录', public: true },
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/AdminCrawlerView.vue'),
        meta: { title: '后台管理' },
      },
      {
        path: 'crawler',
        name: 'AdminCrawler',
        component: () => import('../views/admin/AdminCrawlerView.vue'),
        meta: { title: '手动采集' },
      },
      {
        path: 'backfill',
        name: 'AdminBackfill',
        component: () => import('../views/admin/AdminBackfillView.vue'),
        meta: { title: '历史回补' },
      },
      {
        path: 'issues',
        name: 'AdminIssues',
        component: () => import('../views/admin/AdminIssuesView.vue'),
        meta: { title: '异常中心' },
      },
      {
        path: 'translations',
        name: 'AdminTranslations',
        component: () => import('../views/admin/AdminTranslationsView.vue'),
        meta: { title: '翻译规则管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '首页'} - 星际争霸团战数据平台`

  // 后台路由守卫
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      return { path: '/admin/login', query: { redirect: to.fullPath } }
    }
  }
})

export default router
