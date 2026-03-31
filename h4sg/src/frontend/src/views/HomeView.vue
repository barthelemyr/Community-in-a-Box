<template>
  <div class="p-4">
    <SearchBar @search="handleSearch" />

    <ul class="mt-6">
      <li v-for="book in filteredBooks" :key="book.id" class="p-3 bg-white rounded-2xl my-3">
        {{ book.title }}
      </li>
      <li v-if="filteredBooks.length === 0" class="text-gray-500 italic mt-4">No items found.</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import { useBoxStore } from '@/store/index.js' // Import the component

const boxStore = useBoxStore()

onMounted(async () => {
  await boxStore.fetchAllBooks()
})

// Variable to hold whatever the user typed in the child component
const currentSearchTerm = ref('')

// Function that runs whenever the SearchBar emits a new value
function handleSearch(term) {
  currentSearchTerm.value = term
}

// Automatically filter the list based on the search term
const filteredBooks = computed(() => {
  if (!currentSearchTerm.value) return boxStore.books

  return boxStore.books.filter((book) =>
    book.title.toLowerCase().includes(currentSearchTerm.value.toLowerCase()),
  )
})
</script>
