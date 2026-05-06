<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const menuOpen = ref(false);
</script>

<template>
  <header class="bg-white border-b border-rose-100 sticky top-0 z-50" style="box-shadow: 0 1px 16px rgba(233,30,140,0.07)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-16 sm:h-20">

        <!-- Logo -->
        <a href="/" class="flex items-center gap-3 group">
          <div class="relative">
            <img
              src="/logo.jpeg"
              alt="Studio Bella Mizi"
              class="w-10 h-10 sm:w-12 sm:h-12 rounded-full object-cover ring-2 ring-rose-200 group-hover:ring-rose-400 transition-all duration-300"
            />
            <div class="absolute inset-0 rounded-full bg-rose-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
          <div>
            <span class="block font-display font-semibold text-lg sm:text-xl text-charcoal leading-tight tracking-wide">
              Studio Bella Mizi
            </span>
            <span class="block text-xs text-rose-400 font-body tracking-widest uppercase">
              Beleza &amp; Cuidados
            </span>
          </div>
        </a>

        <!-- Nav desktop -->
        <nav class="hidden sm:flex items-center gap-6">
          <a
            href="/"
            class="text-sm font-body font-medium text-gray-500 hover:text-rose-500 transition-colors duration-200 tracking-wide"
          >
            Catálogo
          </a>
          <a
            href="/admin"
            class="text-sm font-body font-medium text-gray-400 hover:text-rose-400 transition-colors duration-200 border border-rose-100 hover:border-rose-300 px-4 py-1.5 rounded-full"
          >
            Admin
          </a>
        </nav>

        <!-- Mobile admin link -->
        <a
          href="/admin"
          class="sm:hidden text-xs font-body text-gray-400 hover:text-rose-400 transition-colors border border-rose-100 px-3 py-1.5 rounded-full"
        >
          Admin
        </a>

      </div>
    </div>
  </header>
</template>