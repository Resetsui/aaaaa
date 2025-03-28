"""
Módulo para armazenar imagens e ícones em formato base64 ou SVG para uso no streamlit
"""

# Logo principal da guild We Profit
LOGO_SVG = """
<svg width="160" height="120" viewBox="0 0 160 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Escudo dourado com borda brilhante -->
  <g filter="url(#glow)">
    <path d="M80 15L120 45L100 80L80 95L60 80L40 45L80 15Z" fill="#1A1A1A"/>
    <path d="M80 20L115 47L97 77L80 90L63 77L45 47L80 20Z" stroke="#F5B841" stroke-width="3"/>
  </g>

  <!-- Machado de guerra (símbolo simplificado) -->
  <path d="M73 40L77 58L82 40H88L77 75L66 40H73Z" fill="#F5B841" stroke="#F5B841" stroke-width="1"/>
  
  <!-- Nome da Guild abaixo do escudo -->
  <path d="M35 105H39L43 95L47 105H51L43 85H42L35 105Z" fill="#F5B841"/>
  <path d="M53 105H67V102H56V97H65V94H56V88H67V85H53V105Z" fill="#F5B841"/>
  
  <path d="M77 105H81L85 95L89 105H93L85 85H84L77 105Z" fill="#F5B841"/>
  <path d="M95 105H99V97H107V105H111V85H107V94H99V85H95V105Z" fill="#F5B841"/>
  <path d="M113 105H117V94L125 105H129V85H125V96L117 85H113V105Z" fill="#F5B841"/>
  
  <!-- Efeito de brilho dourado -->
  <defs>
    <filter id="glow" x="30" y="5" width="100" height="100" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset/>
      <feGaussianBlur stdDeviation="5"/>
      <feComposite in2="hardAlpha" operator="out"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.961 0 0 0 0 0.722 0 0 0 0 0.255 0 0 0 0.8 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow" result="shape"/>
    </filter>
  </defs>
</svg>
"""

# Ícone simples da guild (só o machado)
ICON_SVG = """
<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Escudo com borda dourada -->
  <g filter="url(#icon_glow)">
    <path d="M30 5L50 25L40 45L30 55L20 45L10 25L30 5Z" fill="#1A1A1A"/>
    <path d="M30 10L45 27L36 44L30 50L24 44L15 27L30 10Z" stroke="#F5B841" stroke-width="2"/>
  </g>
  
  <!-- Machado de guerra simplificado -->
  <path d="M25 20L30 38L35 20H38L30 45L22 20H25Z" fill="#F5B841"/>
  
  <!-- Efeito de brilho dourado -->
  <defs>
    <filter id="icon_glow" x="0" y="0" width="60" height="60" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset/>
      <feGaussianBlur stdDeviation="3"/>
      <feComposite in2="hardAlpha" operator="out"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.961 0 0 0 0 0.722 0 0 0 0 0.255 0 0 0 0.7 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow" result="shape"/>
    </filter>
  </defs>
</svg>
"""