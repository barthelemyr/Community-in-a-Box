<template>
  <div class="min-h-screen flex flex-col px-5 pb-10 pt-4 gap-4">
    <!-- Title + count -->
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0 flex-1">
        <FitTitle style="color: #e87d4a">{{ t('bookList') }}</FitTitle>
      </div>
      <div class="text-right flex-shrink-0 pt-1">
        <span class="font-black text-3xl" style="color: #2a7a6e">{{ books.length }}</span>
        <p class="text-xs font-medium text-gray-500 leading-tight">{{ t('bookListPage.total') }}</p>
      </div>
    </div>

    <!-- Search -->
    <input
      v-model="searchTerm"
      type="text"
      :placeholder="t('bookListPage.search')"
      class="w-full rounded-2xl px-4 py-3 text-gray-900 font-medium border-2 border-gray-700 bg-white/60 focus:outline-none focus:bg-white/80"
    />

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div
        class="w-10 h-10 border-4 border-gray-400 border-t-transparent rounded-full animate-spin"
      ></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 rounded-xl p-4 text-center">
      <p class="text-red-700 font-semibold text-sm">{{ error }}</p>
    </div>

    <!-- Book list -->
    <ul v-else class="flex flex-col gap-2">
      <li
        v-for="book in filteredBooks"
        :key="book.isbn"
        class="bg-white/60 rounded-xl px-4 py-3 flex items-start gap-3"
      >
        <div class="min-w-0 flex-1">
          <p class="font-bold text-gray-900 truncate">{{ book.title }}</p>
          <p class="text-xs text-gray-500 truncate">{{ book.author }}</p>
        </div>
        <p
          class="text-xs font-mono flex-shrink-0 pt-0.5"
          :class="isOld(book.last_scanned) ? 'text-red-500 font-bold' : 'text-gray-400'"
        >
          {{ formatDate(book.last_scanned) }}
        </p>
      </li>

      <li v-if="filteredBooks.length === 0" class="text-gray-500 italic text-center py-6">
        {{ t('bookListPage.noResults') }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLocale } from '../composables/useLocale.js'
import FitTitle from '../components/FitTitle.vue'
import { useBoxStore } from '@/store/index.js'

const route = useRoute()
const { t } = useLocale()
const boxId = route.params.id
const boxStore = useBoxStore()

const books = ref([])
const loading = ref(true)
const error = ref('')
const searchTerm = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''

  try {
    const fetchedBooks = await boxStore.fetchBoxBooksById(boxId)

    if (fetchedBooks) {
      books.value = fetchedBooks
    }
  } catch (err) {
    error.value = 'Failed to load books.'
    console.error(err)
  } finally {
    loading.value = false
  }
})

const filteredBooks = computed(() => {
  console.log(books.value)
  if (!searchTerm.value.trim()) return books.value

  const q = searchTerm.value.toLowerCase()
  return books.value.filter(
    (b) =>
      b.title?.toLowerCase().includes(q) ||
      b.author?.toLowerCase().includes(q) ||
      b.isbn?.includes(q),
  )
})

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString(undefined, {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  })
}

function isOld(dt) {
  if (!dt) return false
  const THREE_WEEKS = 21 * 24 * 60 * 60 * 1000
  return Date.now() - new Date(dt).getTime() > THREE_WEEKS
}
</script>
