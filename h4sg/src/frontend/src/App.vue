<template>
  <div :class="['app-layout', currentBgClass]">
    <main>
      <h4>Community-in-a-box</h4>
      <nav>
        <router-link to="/">Home</router-link>
      </nav>
    </main>
    <RouterView />
    <footer></footer>
  </div>
</template>

<script setup>
// 2. Imported useRoute and computed
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'

// 3. Setup the route and the computed property
const route = useRoute()

const currentBgClass = computed(() => {
  // Returns the class from your router, or a default empty string/class if none is set
  return route.meta.bgClass || ''
})
</script>

<style>
/* Add a smooth transition so the color fades nicely when you click links */
.app-layout {
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

/* Define your purple class somewhere in your CSS! */
.page-purple {
  background-color: #e6e6fa; /* Or whatever purple you like */
}
</style>
