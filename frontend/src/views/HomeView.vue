<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <p class="hero-greeting">你好，欢迎来到</p>
      <h1 class="hero-title">
        StarCraft<br/>
        <span class="hero-accent">团战数据</span>
      </h1>
      <p class="hero-desc">
        实时追踪星际争霸团战比赛、选手表现与排行榜数据。
      </p>
      <div class="hero-cta">
        <router-link to="/matches" class="cta-button">查看比赛</router-link>
      </div>
    </section>

    <!-- 统计概览 -->
    <section class="stats-section">
      <span class="section-number">01.</span>
      <h2 class="section-heading">数据概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">总比赛数</div>
          <div class="stat-value">{{ summary.total_matches ?? '—' }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">选手总数</div>
          <div class="stat-value">{{ summary.total_players ?? '—' }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">队伍总数</div>
          <div class="stat-value">{{ summary.total_teams ?? '—' }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最近比赛</div>
          <div class="stat-value stat-value--sm">{{ summary.latest_match_date ?? '—' }}</div>
        </div>
      </div>
    </section>

    <!-- 最新比赛 -->
    <section class="matches-section">
      <div class="section-header">
        <div>
          <span class="section-number">02.</span>
          <h2 class="section-heading">最新比赛</h2>
        </div>
        <router-link to="/matches" class="section-link">查看全部 →</router-link>
      </div>
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="28"><Loading /></el-icon>
      </div>
      <div v-else-if="latestMatches.length === 0" class="empty-state">暂无比赛数据</div>
      <div v-else class="match-list">
        <router-link
          v-for="match in latestMatches"
          :key="match.id"
          :to="`/matches/${match.id}`"
          class="match-item"
        >
          <span class="match-bullet"></span>
          <span class="match-date">{{ match.match_date }}</span>
          <span class="match-title">{{ match.title }}</span>
          <span class="match-arrow">→</span>
        </router-link>
      </div>
    </section>

    <!-- 排行榜 -->
    <section class="ranking-section">
      <div class="ranking-grid">
        <!-- 奖金排行 -->
        <div class="ranking-block">
          <div class="section-header">
            <div>
              <span class="section-number">03.</span>
              <h2 class="section-heading">奖金排行</h2>
            </div>
            <router-link to="/rankings" class="section-link">更多 →</router-link>
          </div>
          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>
          <div v-else-if="prizeRanking.length === 0" class="empty-state">暂无数据</div>
          <div v-else class="ranking-list">
            <div v-for="(item, idx) in prizeRanking" :key="idx" class="ranking-item">
              <span class="ranking-pos">{{ String(idx + 1).padStart(2, '0') }}</span>
              <router-link :to="`/players/${item.player_id}`" class="ranking-name">{{ item.player_name }}</router-link>
              <span class="ranking-value prize">{{ formatPrize(item.total_prize) }}</span>
            </div>
          </div>
        </div>

        <!-- 连胜排行 -->
        <div class="ranking-block">
          <div class="section-header">
            <div>
              <span class="section-number">04.</span>
              <h2 class="section-heading">连胜排行</h2>
            </div>
          </div>
          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>
          <div v-else-if="streakRanking.length === 0" class="empty-state">暂无数据</div>
          <div v-else class="ranking-list">
            <div v-for="(item, idx) in streakRanking" :key="idx" class="ranking-item">
              <span class="ranking-pos">{{ String(idx + 1).padStart(2, '0') }}</span>
              <router-link :to="`/players/${item.player_id}`" class="ranking-name">{{ item.player_name }}</router-link>
              <span class="ranking-value streak">{{ item.max_streak }}连胜</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getDashboardSummary, getLatestMatches, getPrizeRanking, getWinStreakRanking } from '../api/dashboard'

const summary = ref({})
const latestMatches = ref([])
const prizeRanking = ref([])
const streakRanking = ref([])
const loading = ref(true)

function formatPrize(val) {
  if (!val) return '₩0'
  return '₩' + Number(val).toLocaleString()
}

onMounted(async () => {
  try {
    const [summaryRes, matchesRes, prizeRes, streakRes] = await Promise.allSettled([
      getDashboardSummary(),
      getLatestMatches(10),
      getPrizeRanking(10),
      getWinStreakRanking(10),
    ])
    if (summaryRes.status === 'fulfilled') summary.value = summaryRes.value || {}
    if (matchesRes.status === 'fulfilled') latestMatches.value = matchesRes.value?.items || matchesRes.value || []
    if (prizeRes.status === 'fulfilled') prizeRanking.value = prizeRes.value || []
    if (streakRes.status === 'fulfilled') streakRanking.value = streakRes.value || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 100px;
  padding-top: 80px;
  padding-bottom: 60px;
}

/* ── Hero ── */
.hero {
  max-width: 640px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.hero-greeting {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 20px;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 60px;
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: -2px;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.hero-accent {
  color: var(--accent);
}

.hero-desc {
  font-family: var(--font-body);
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 40px;
  max-width: 500px;
}

.cta-button {
  display: inline-block;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  padding: 14px 32px;
  transition: all 0.25s var(--ease-smooth);
}

.cta-button:hover {
  background: var(--accent-deep);
  transform: translateY(-2px);
  box-shadow: var(--glow-accent);
}

/* ── Stats Grid ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

/* ── Match List ── */
.match-list {
  display: flex;
  flex-direction: column;
}

.match-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.25s var(--ease-smooth);
}

.match-item:hover {
  background: var(--bg-card-hover);
}

.match-bullet {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.25s var(--ease-smooth);
}

.match-item:hover .match-bullet {
  opacity: 1;
}

.match-date {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
  min-width: 86px;
}

.match-title {
  flex: 1;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.match-arrow {
  color: var(--text-muted);
  font-size: 14px;
  transition: all 0.25s var(--ease-smooth);
}

.match-item:hover .match-arrow {
  color: var(--accent);
  transform: translateX(4px);
}

/* ── Ranking Grid ── */
.ranking-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  transition: background 0.25s var(--ease-smooth);
}

.ranking-item:hover {
  background: var(--bg-card-hover);
}

.ranking-pos {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  min-width: 24px;
}

.ranking-name {
  flex: 1;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-primary);
  text-decoration: none;
  transition: color 0.25s var(--ease-smooth);
}

.ranking-name:hover {
  color: var(--accent);
}

.ranking-value {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
}

.ranking-value.prize { color: var(--color-prize); }
.ranking-value.streak { color: var(--color-streak); }

/* ── Loading / Empty ── */
.loading-container {
  display: flex;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-muted);
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-dim);
  font-family: var(--font-display);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

@media (max-width: 768px) {
  .hero-title { font-size: 42px; letter-spacing: -1px; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .ranking-grid { grid-template-columns: 1fr; }
  .home { gap: 72px; padding-top: 48px; }
}
</style>
