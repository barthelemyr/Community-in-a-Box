<template>
  <div class="min-h-screen flex flex-col" style="background-color: #F5D85E;">

    <!-- Language switcher -->
    <div class="flex justify-end px-5 pt-4 pb-2">
      <nav class="flex items-center gap-1 font-bold text-sm text-gray-900">
        <template v-for="(lang, i) in languages" :key="lang">
          <button
            @click="currentLang = lang"
            :class="currentLang === lang ? 'font-black underline' : 'font-bold underline opacity-70 hover:opacity-100'"
            class="transition-opacity"
          >{{ lang }}</button>
          <span v-if="i < languages.length - 1" class="opacity-60 select-none">|</span>
        </template>
      </nav>
    </div>

    <!-- Error state -->
    <div v-if="error" class="flex-1 flex items-center justify-center p-8">
      <p class="text-xl font-bold text-gray-800 text-center">{{ error }}</p>
    </div>

    <!-- Main content -->
    <div v-else class="flex-1 flex flex-col lg:flex-row items-start gap-4 px-5 pb-8 lg:px-10 lg:gap-8">

      <!-- Left column: title + (mobile photo) + buttons -->
      <div class="flex-1 flex flex-col gap-4 w-full">

        <!-- Box title & address -->
        <div>
          <p class="text-sm font-semibold tracking-wide" style="color: #2a7a6e;">
            Public Library Bienne
          </p>
          <h1
            class="text-white font-black uppercase leading-none"
            style="font-size: clamp(3rem, 15vw, 7rem); letter-spacing: 0.04em;"
          >
            BOX №{{ boxId }}
          </h1>
          <p class="font-black uppercase tracking-wider text-gray-800 mt-1"
             style="font-size: clamp(0.85rem, 3.5vw, 1.2rem);">
            Adresse: {{ boxAddress }}
          </p>
        </div>

        <!-- Photo — shown here (between title and buttons) on mobile only -->
        <div class="lg:hidden w-full">
          <img
            src="/box-photo.png"
            alt="Community book box"
            class="w-full rounded-2xl shadow-lg object-cover"
            style="max-height: 240px; object-position: center;"
            onerror="this.parentElement.style.display='none'"
          />
        </div>

        <!-- Navigation buttons 2×3 grid -->
        <div class="grid grid-cols-2 gap-3 w-full max-w-md">

          <button
            v-for="btn in purpleButtons" :key="btn.name"
            @click="navigate(btn.route)"
            class="rounded-2xl py-5 px-3 font-bold uppercase tracking-wider text-gray-800 hover:opacity-90 active:scale-95 transition-all shadow-sm"
            style="background-color: #A89FD8; font-size: clamp(0.7rem, 3vw, 0.9rem);"
          >{{ btn.label }}</button>

          <button
            v-for="btn in orangeButtons" :key="btn.name"
            @click="navigate(btn.route)"
            class="rounded-2xl py-5 px-3 font-bold uppercase tracking-wider text-gray-800 hover:opacity-90 active:scale-95 transition-all shadow-sm"
            style="background-color: #E87D4A; font-size: clamp(0.7rem, 3vw, 0.9rem);"
          >{{ btn.label }}</button>

          <button
            v-for="btn in creamButtons" :key="btn.name"
            @click="navigate(btn.route)"
            class="rounded-2xl py-5 px-3 font-bold uppercase tracking-wider text-gray-800 border-2 border-gray-800 hover:bg-white/50 active:scale-95 transition-all"
            style="background-color: #F5F0E0; font-size: clamp(0.7rem, 3vw, 0.9rem);"
          >{{ btn.label }}</button>

        </div>
      </div>

      <!-- Photo — shown on the right on desktop (lg+) only -->
      <div class="hidden lg:flex lg:items-start lg:justify-end lg:flex-shrink-0 lg:pt-2" style="width: min(45%, 400px);">
        <img
          src="/box-photo.png"
          alt="Community book box"
          class="w-full rounded-2xl shadow-lg object-cover"
          style="max-height: 520px;"
          onerror="this.parentElement.style.display='none'"
        />
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

// Mock API — replace with real fetch once backend /boxes/{id} endpoint exists
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
  { name: 'add-book', label: 'Add Book',    route: 'add-book' },
  { name: 'borrow',   label: 'Borrow Book', route: 'borrow' },
]
const orangeButtons = [
  { name: 'book-list', label: 'Book List',       route: 'book-list' },
  { name: 'book-info', label: 'Info About Book',  route: 'book-info' },
]
const creamButtons = [
  { name: 'games', label: 'Games',            route: 'games' },
  { name: 'help',  label: 'Help the Library', route: 'help' },
]

function navigate(routeName) {
  router.push({ name: routeName, params: { id: boxId.value } })
}
</script>
