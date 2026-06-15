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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '首页'} - 星际争霸团战数据平台`
})

export default router
