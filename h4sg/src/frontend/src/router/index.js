import { createRouter, createWebHistory } from 'vue-router'
import BoxView from '../views/BoxView.vue'
import PlaceholderView from '../views/PlaceholderView.vue'
import AddBook from '../views/AddBook.vue'
import BookList from '@/views/BookList.vue'
import RemoveBook from '../views/RemoveBook.vue'
import InfoAboutBook from '../views/InfoAboutBook.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Redirect bare domain to a landing or catch-all — no box selected
    { path: '/', redirect: '/box' },

    // Box home — QR code points here: /box/4
    { path: '/box/:id', name: 'home', component: BoxView, meta: { bgClass: 'page-yellow' } },

    // Actions scoped to a specific box
    { path: '/box/:id/add', name: 'add', component: AddBook, meta: { bgClass: 'page-purple' } },
    {
      path: '/box/:id/borrow',
      name: 'borrow',
      component: RemoveBook,
      meta: { bgClass: 'page-purple' },
    },
    {
      path: '/box/:id/books',
      name: 'books',
      component: BookList,
      meta: { bgClass: 'page-purple' },
    },
    {
      path: '/box/:id/info',
      name: 'info',
      component: InfoAboutBook,
      meta: { bgClass: 'page-orange' },
    },
    {
      path: '/box/:id/games',
      name: 'games',
      component: PlaceholderView,
      meta: { bgClass: 'page-cream' },
    },
    {
      path: '/box/:id/help',
      name: 'help',
      component: PlaceholderView,
      meta: { bgClass: 'page-cream' },
    },

    // Catch-all: unknown routes redirect to /box
    { path: '/:pathMatch(.*)*', redirect: '/box' },
  ],
})

export default router
