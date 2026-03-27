<template>
  <div class="wrapper">
    <main>
      <h4>Community-in-a-box</h4>
      <nav>
        <router-link to="/">Home</router-link>
      </nav>
    </main>
    <footer></footer>
  </div>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>
