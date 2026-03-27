<template>
  <div class="min-h-screen flex flex-col" style="background-color: #F5D85E;">
    <!-- Language switcher -->
    <div class="flex justify-end p-4">
      <nav class="flex gap-2 font-bold text-sm">
        <button
          v-for="lang in languages"
          :key="lang"
          @click="currentLang = lang"
          :class="[
            'underline hover:opacity-70 transition-opacity',
            currentLang === lang ? 'font-black' : 'font-bold',
          ]"
        >
          {{ lang }}
        </button>
        <span class="mx-1 text-gray-700" v-if="languages.indexOf(lang) < languages.length - 1"></span>
      </nav>
    </div>

    <!-- Main content -->
    <div v-if="error" class="flex-1 flex items-center justify-center p-8">
      <p class="text-2xl font-bold text-gray-800">{{ error }}</p>
    </div>

    <div v-else class="flex-1 flex flex-col md:flex-row items-start gap-6 px-6 pb-8 md:px-10">
      <!-- Left column: title + buttons -->
      <div class="flex-1 flex flex-col gap-4">
        <!-- Box header -->
        <div class="mb-2">
          <p class="text-center text-sm font-medium" style="color: #2a7a6e;">Public Library Bienne</p>
          <h1 class="text-white font-black uppercase tracking-widest leading-none"
              style="font-size: clamp(3rem, 12vw, 7rem);">
            BOX №{{ boxId }}
          </h1>
          <p class="font-black uppercase tracking-wider text-gray-800 text-lg md:text-xl mt-1">
            Adresse: {{ boxAddress }}
          </p>
        </div>

        <!-- Navigation buttons 2×3 grid -->
        <div class="grid grid-cols-2 gap-3 w-full max-w-lg">
          <!-- Row 1: purple -->
          <button
            v-for="btn in purpleButtons"
            :key="btn.name"
            @click="navigate(btn.route)"
            class="rounded-2xl py-5 px-4 font-bold uppercase tracking-wider text-sm md:text-base text-gray-800 hover:opacity-90 active:scale-95 transition-all shadow-sm"
            style="background-color: #A89FD8;"
          >
            {{ btn.label }}
          </button>

          <!-- Row 2: orange -->
          <button
            v-for="btn in orangeButtons"
            :key="btn.name"
            @click="navigate(btn.route)"
            class="rounded-2xl py-5 px-4 font-bold uppercase tracking-wider text-sm md:text-base text-gray-800 hover:opacity-90 active:scale-95 transition-all shadow-sm"
            style="background-color: #E87D4A;"
          >
            {{ btn.label }}
          </button>

          <!-- Row 3: cream/white -->
          <button
            v-for="btn in creamButtons"
            :key="btn.name"
            @click="navigate(btn.route)"
            class="rounded-2xl py-5 px-4 font-bold uppercase tracking-wider text-sm md:text-base text-gray-800 border-2 border-gray-800 hover:bg-white/50 active:scale-95 transition-all"
            style="background-color: #F5F0E0;"
          >
            {{ btn.label }}
          </button>
        </div>
      </div>

    
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const boxId = ref(null)
const boxAddress = ref('')
const error = ref(null)
const currentLang = ref('EN')
const languages = ['DE', 'FR', 'EN']

// Mock API — replace with real fetch once backend endpoint exists
function fetchBoxInfo(id) {
  const mockBoxes = {
    1: 'Hauptstrasse 1, Bienne',
    2: 'Bahnhofplatz 3, Bienne',
    3: 'Rue de Nidau 12, Bienne',
    4: 'Switzerland, Bienne',
    42: 'Musterstrasse 5, Bienne',
  }
  return mockBoxes[id] ?? `Box ${id} location`
}

onMounted(() => {
  const id = route.query.box
  if (!id) {
    error.value = 'No box ID found. Please scan a QR code on a book box.'
    return
  }
  boxId.value = id
  boxAddress.value = fetchBoxInfo(Number(id))
})

const purpleButtons = [
  { name: 'add-book',  label: 'Add Book',    route: 'add-book' },
  { name: 'borrow',    label: 'Borrow Book', route: 'borrow' },
]
const orangeButtons = [
  { name: 'book-list', label: 'Book List',      route: 'book-list' },
  { name: 'book-info', label: 'Info About Book', route: 'book-info' },
]
const creamButtons = [
  { name: 'games', label: 'Games',           route: 'games' },
  { name: 'help',  label: 'Help the Library', route: 'help' },
]

function navigate(routeName) {
  router.push({ name: routeName, params: { id: boxId.value } })
}
</script>