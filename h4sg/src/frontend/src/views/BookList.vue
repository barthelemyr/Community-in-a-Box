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
import { ref, computed } from 'vue'
import SearchBar from '@/components/SearchBar.vue' // Import the component

// Mock data
const books = ref([
  { id: 1, title: 'The Hobbit' },
  { id: 2, title: 'Dune' },
  { id: 3, title: '1984' },
])

// Variable to hold whatever the user typed in the child component
const currentSearchTerm = ref('')

// Function that runs whenever the SearchBar emits a new value
function handleSearch(term) {
  currentSearchTerm.value = term
}

// Automatically filter the list based on the search term
const filteredBooks = computed(() => {
  if (!currentSearchTerm.value) return books.value

  return books.value.filter((book) =>
    book.title.toLowerCase().includes(currentSearchTerm.value.toLowerCase()),
  )
})
</script>
