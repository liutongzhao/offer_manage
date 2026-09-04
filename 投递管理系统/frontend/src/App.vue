<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <el-container class="app-shell">
    <el-aside width="210px" class="app-aside">
      <div class="app-logo">秋招投递管理</div>
      <el-menu
        :default-active="route.path"
        router
        class="app-menu"
        background-color="#1f2937"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/">
          <el-icon><DataLine /></el-icon>
          <span>投递看板</span>
        </el-menu-item>
        <el-menu-item index="/companies">
          <el-icon><OfficeBuilding /></el-icon>
          <span>公司管理</span>
        </el-menu-item>
        <el-menu-item index="/applications">
          <el-icon><Promotion /></el-icon>
          <span>投递记录</span>
        </el-menu-item>
        <el-menu-item index="/issues">
          <el-icon><Warning /></el-icon>
          <span>问题记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <span class="app-crumb">{{ route.meta.title || '秋招投递管理平台' }}</span>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-shell {
  height: 100%;
}

.app-aside {
  background: #1f2937;
}

.app-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1px;
  background: #111827;
}

.app-menu {
  border-right: none;
}

.app-header {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.app-crumb {
  font-size: 15px;
  font-weight: 600;
}

.app-main {
  padding: 18px;
}
</style>
