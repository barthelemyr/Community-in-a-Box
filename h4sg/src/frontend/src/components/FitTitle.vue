<template>
  <component
    :is="tag"
    ref="el"
    class="font-black uppercase leading-none w-full block"
    style="overflow-wrap: break-word; word-break: break-word; white-space: pre-line;"
  >
    <slot />
  </component>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  tag: { type: String, default: 'h1' },
  max: { type: Number, default: 80 },
  min: { type: Number, default: 12 },
})

const el = ref(null)

function fit() {
  const node = el.value
  if (!node) return
  const parent = node.parentElement
  if (!parent) return
  const available = parent.clientWidth
  if (!available) return

  // Measure natural width at max size with nowrap (br still breaks, \n is collapsed)
  node.style.fontSize = props.max + 'px'
  node.style.whiteSpace = 'nowrap'
  const natural = node.scrollWidth
  node.style.whiteSpace = 'pre-line'

  const size = natural > available
    ? Math.max(props.min, Math.floor(props.max * (available / natural)))
    : props.max

  node.style.fontSize = size + 'px'
}

let ro
onMounted(async () => {
  await nextTick()
  fit()
  ro = new ResizeObserver(fit)
  if (el.value?.parentElement) ro.observe(el.value.parentElement)
})
onUnmounted(() => ro?.disconnect())
</script>
