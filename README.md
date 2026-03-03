# Clarvix Landing - Digital Services Agency

Landing page profesional para Clarvix, agencia de servicios digitales con enfoque en:
- **Auditoría de Presencia Digital**
- **Generación de Leads B2B**

## 🌍 Idiomas Soportados

- **Hebreo** (עברית) - Primario para Israel
- **Árabe** (العربية) - Secundario para Israel
- **Inglés** (English) - Para mercados internacionales

## 🎯 Características

### 1. Auditoría de Presencia Digital
- **Paquete Básico**: ₪185
  - Dórah SEO básico
  - Análisis de redes sociales

- **Paquete Estándar**: ₪370
  - Dórah SEO detallado
  - Análisis competitivo
  - Recomendaciones de mejora

- **Paquete Premium**: ₪555
  - Dórah SEO completo
  - Análisis competitivo profundo
  - Plan de acción 90 días
  - Consultoría directa

### 2. Generación de Leads B2B
- **Paquete Starter**: ₪9,250/mes
  - 10-15 leads calificados
  - Reportes mensuales
  - Hebreo y árabe

- **Paquete Professional**: ₪18,500/mes
  - 20-30 leads calificados
  - Reportes semanales
  - Análisis competitivo
  - Hebreo y árabe

- **Paquete Enterprise**: ₪37,000/mes
  - 40-60 leads calificados
  - Reportes diarios
  - Análisis competitivo profundo
  - Consultoría directa
  - Hebreo y árabe

## 💳 Integración de Pagos

### Payoneer
- Pasarela de pagos principal
- Comisión: 2%
- Dinero directo a banco israelí
- Setup: 24 horas

### Paddle (Próximamente)
- Alternativa profesional
- Comisión: 2.5%
- Mejor facturación
- Setup: 3-5 días

## 🚀 Inicio Rápido

### Instalación
```bash
git clone https://github.com/Titus9123/clarvix-landing.git
cd clarvix-landing
```

### Uso Local
```bash
# Abrir en navegador
open index.html
# O usar un servidor local
python -m http.server 8000
```

### Configuración de Payoneer
1. Obtener Merchant ID de Payoneer
2. Reemplazar `YOUR_PAYONEER_MERCHANT_ID` en `app.js`
3. Configurar webhook URL en Payoneer

## 📁 Estructura de Archivos

```
clarvix-landing/
├── index.html           # Página principal
├── styles.css           # Estilos
├── app.js              # Lógica de JavaScript
├── translations.js     # Traducciones (HE/AR/EN)
├── README.md           # Este archivo
└── .gitignore          # Archivos a ignorar
```

## 🔧 Configuración

### Variables de Entorno
```javascript
// En app.js, reemplazar:
'merchant_id': 'YOUR_PAYONEER_MERCHANT_ID'
```

### Webhook de Payoneer
```
POST /webhook/payoneer
{
  "merchant_id": "...",
  "transaction_id": "...",
  "amount": 9250,
  "currency": "ILS",
  "status": "completed"
}
```

## 📊 Flujo de Pago

```
Cliente hace clic en "Checkout"
    ↓
Completa email
    ↓
Redirigido a Payoneer
    ↓
Completa pago
    ↓
Webhook confirma pago
    ↓
Email de confirmación
    ↓
Acceso a servicio
```

## 🌐 Despliegue

### GitHub Pages
```bash
git push origin main
# Activar GitHub Pages en Settings
```

### Netlify
```bash
npm install -g netlify-cli
netlify deploy
```

### Vercel
```bash
npm install -g vercel
vercel
```

## 📧 Email Marketing

### Campañas Automáticas
1. **Bienvenida** - Después de compra
2. **Agradecimiento** - 24 horas después
3. **Upsell** - 7 días después
4. **Seguimiento** - 30 días después

## 📱 Responsividad

- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

## ♿ Accesibilidad

- ✅ WCAG 2.1 AA
- ✅ Soporte para lectores de pantalla
- ✅ Navegación por teclado

## 🔒 Seguridad

- ✅ HTTPS requerido
- ✅ Validación de formularios
- ✅ Protección CSRF
- ✅ Encriptación de datos

## 📈 SEO

- ✅ Meta tags optimizados
- ✅ Schema.org markup
- ✅ Sitemap.xml
- ✅ robots.txt

## 🐛 Reportar Bugs

Crear issue en GitHub con:
- Descripción del bug
- Pasos para reproducir
- Navegador y versión
- Screenshots si es posible

## 📝 Changelog

### v1.0.0 (2026-03-03)
- ✅ Landing inicial
- ✅ Integración Payoneer
- ✅ Multiidioma (HE/AR/EN)
- ✅ Carrito de compras
- ✅ Contacto

### v1.1.0 (Próximamente)
- 🔄 Integración Paddle
- 🔄 Email marketing
- 🔄 CRM integration
- 🔄 Analytics

## 📞 Soporte

- Email: contact@clarvix.net
- WhatsApp: [Tu número]
- Telegram: [Tu usuario]

## 📄 Licencia

© 2026 Clarvix. Todos los derechos reservados.

## 👨‍💼 Autor

**Albert Neumann**
- Email: contact@clarvix.net
- Website: https://clarvix.net

---

**Última actualización:** 2026-03-03
**Versión:** 1.0.0
