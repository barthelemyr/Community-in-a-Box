import { ref, computed } from 'vue'
import en from '../locales/en.json'
import de from '../locales/de.json'
import fr from '../locales/fr.json'

const locales = { en, de, fr }
const STORAGE_KEY = 'ciab-lang'

// Shared state — one instance across the whole app
const currentLang = ref(localStorage.getItem(STORAGE_KEY) ?? 'en')

export function useLocale() {
  function setLang(lang) {
    currentLang.value = lang.toLowerCase()
    localStorage.setItem(STORAGE_KEY, currentLang.value)
  }

  // t('addBook') → looks up key in the active locale, falls back to English
  function t(key) {
    const locale = locales[currentLang.value] ?? en
    // Support nested keys like 'pages.add'
    return key.split('.').reduce((obj, k) => obj?.[k], locale) ?? key
  }

  const languages = [
    { code: 'de', label: 'DE' },
    { code: 'fr', label: 'FR' },
    { code: 'en', label: 'EN' },
  ]

  return {
    currentLang: computed(() => currentLang.value),
    languages,
    setLang,
    t,
  }
}