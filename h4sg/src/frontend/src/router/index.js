import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlaceholderView from '../views/PlaceholderView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                    name: 'home',      component: HomeView },
    { path: '/box/:id/add-book',    name: 'add-book',  component: PlaceholderView },
    { path: '/box/:id/borrow',      name: 'borrow',    component: PlaceholderView },
    { path: '/box/:id/book-list',   name: 'book-list', component: PlaceholderView },
    { path: '/box/:id/book-info',   name: 'book-info', component: PlaceholderView },
    { path: '/box/:id/games',       name: 'games',     component: PlaceholderView },
    { path: '/box/:id/help',        name: 'help',      component: PlaceholderView },
  ],
})

export default router