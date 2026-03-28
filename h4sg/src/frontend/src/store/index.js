import { defineStore } from 'pinia'

export const useBoxStore = defineStore('boxStore', {
  state: () => ({
    boxes: [],
    books: [],
  }),

  getters: {
    getBox: (state) => {
      return (id) => state.boxes.find((box) => box.id == id)
    },

    getAllBooks: (state) => {
      return state.books
    },
  },

  actions: {
    async fetchBoxById(id) {
      const existingBox = this.boxes.find((box) => box.id == id)

      if (existingBox) {
        console.log(`Box ${id} loaded from Pinia cache!`)
        return existingBox
      }

      try {
        console.log(`Fetching Box ${id} from API...`)

        const response = await fetch(`/api/shelves/${id}/books`)

        if (!response.ok) throw new Error('Network response was not ok')

        const newBox = await response.json()

        this.boxes.push(newBox)

        return newBox
      } catch (error) {
        console.error(`Failed to fetch box ${id}:`, error)
      }
    },

    async fetchAllBooks() {
      if (this.books.length > 0) {
        console.log('Books loaded from Pinia cache!')
        return this.books
      }

      try {
        console.log('Fetching books from API...')
        const response = await fetch('/api/shelves/books')

        if (!response.ok) throw new Error('Network response was not ok')

        const data = await response.json()

        this.books = data.flatMap(box => box.books)

        return this.books
      } catch (error) {
        console.error('Failed to fetch books:', error)
      }
    },
  },
})
