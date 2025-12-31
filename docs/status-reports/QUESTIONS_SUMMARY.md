# 📋 Resumen de Preguntas de Onboarding

**Total**: 48 preguntas  
**Etapas**: 4 (Quick Start, Team & Tech, Identity & Brand, Digital & Growth)

---

## 🎯 ETAPA 1: Quick Start (9 preguntas)
**Objetivo**: Información esencial para empezar

| ID | Pregunta | Tipo | Campo DB |
|----|----------|------|----------|
| Q1 | What is your full name? | Short Text | `q1_admin` |
| Q2 | What is your birthday? (Month & day only) | Short Text | `q2_culture` |
| Q3 | What is your practice name (legal)? | Short Text | `q3_legal` |
| Q4 | What is your practice EIN? | Short Text | `q4_legal` |
| Q5 | What is your office mailing address? | Long Text | `q5_admin` |
| Q6 | What is your home mailing address? (opcional) | Long Text | `q6_admin` |
| Q7 | What is your office phone number? | Short Text | `q7_suite_setup` |
| Q8 | What is your office texting line? | Short Text | `q8_suite_setup` |
| Q9 | What is the best email for correspondence? | Email | `q9_admin` |

---

## 👥 ETAPA 2: Team & Tech (7 preguntas)
**Objetivo**: Estructura del equipo y configuración técnica

| ID | Pregunta | Tipo | Dependencia | Campo DB |
|----|----------|------|-------------|----------|
| Q10 | Please list members of your team and their roles | Long Text | - | `q10_team` |
| Q11 | Who will be the ONE point person? | Short Text | - | `q11_client_lead` |
| Q12 | How do you prefer to communicate? | Multiple Choice | - | `q12_communication` |
| Q13 | On a scale of 1-5, how tech-savvy do you feel? | Scale | - | `q13_readiness` |
| Q14 | Are you working with a marketing company? | Yes/No | - | `q14_marketing` |
| Q15 | If yes, who are you working with? | Short Text | **Q14=Yes** | `q15_marketing` |
| Q16 | Do you use any software for texting/email? | Long Text | - | `q16_stack` |

**Opciones Q12**: Slack, Email, Practice Suite

---

## 🎨 ETAPA 3: Identity & Brand (12 preguntas)
**Objetivo**: Personalidad de la práctica e identidad visual

| ID | Pregunta | Tipo | Campo DB |
|----|----------|------|----------|
| Q17 | What type of practice are you? | Multiple Choice | `q17_practice_type` |
| Q18 | Who do you most love working with? | Long Text | `q18_ideal_client` |
| Q19 | Who do you NOT want more of? | Long Text | `q19_boundaries` |
| Q20 | What problem do people come to you for first? | Long Text | `q20_messaging` |
| Q21 | What transformation do they stay for? | Long Text | `q21_messaging` |
| Q22 | Choose 3-5 words that describe your practice | Long Text | `q22_brand_voice` |
| Q23 | Choose 3-5 words you NEVER want to sound like | Long Text | `q23_brand_voice` |
| Q24 | Do you have a brand kit you're happy with? | Multiple Choice | `q24_brand` |
| Q25 | Do you currently have a logo? | Yes/No | `q25_brand` |
| Q26 | Do you have a font set? | Yes/No | `q26_brand` |
| Q27 | Do you have a color palette? | Yes/No | `q27_brand` |
| Q28 | Where are your brand assets stored? | Multiple Choice | `q28_brand` |

**Opciones Q17**: Chiro, PT, Therapy, Acupuncture, Naturopathic, Other  
**Opciones Q24**: Yes, It's okay, No  
**Opciones Q28**: Canva, Google Drive, Dropbox, Not sure

---

## 🌐 ETAPA 4: Digital & Growth (20 preguntas)
**Objetivo**: Presencia online y estrategia de crecimiento

### Website (5 preguntas)
| ID | Pregunta | Tipo | Dependencia | Campo DB |
|----|----------|------|-------------|----------|
| Q29 | Do you currently have a website? | Multiple Choice | - | `q29_website` |
| Q30 | What would you like to do with your website? | Multiple Choice | **Q29≠No** | `q30_website` |
| Q31 | Would you like us to build a new website? | Yes/No | **Q29=No** | `q31_website` |
| Q32 | What is the main job your website should do? | Multiple Choice | - | `q32_website_strategy` |
| Q33 | What currently bothers you about your website? | Long Text | **Q29≠No** | `q33_website` |

**Opciones Q29**: Yes, No, Sort of  
**Opciones Q30**: Leave as-is, Light updates, Refresh, Full rebuild, Need guidance  
**Opciones Q32**: Booking, Education, Trust, Referrals, All

### Social Media (5 preguntas)
| ID | Pregunta | Tipo | Dependencia | Campo DB |
|----|----------|------|-------------|----------|
| Q34 | Which platforms do you want to grow with? | Multi-Select | - | `q34_social` |
| Q35 | How should Instagram function? | Multiple Choice | **Instagram selected** | `q35_social_ig` |
| Q36 | What role should Facebook play? | Multiple Choice | **Facebook selected** | `q36_social_fb` |
| Q37 | Who would LinkedIn be for? | Short Text | **LinkedIn selected** | `q37_social_li` |
| Q38 | What would a blog support? | Multiple Choice | **Blog selected** | `q38_blog` |

**Opciones Q34**: Instagram, Facebook, LinkedIn, Blog, None  
**Opciones Q35**: Trust, Education, Visibility, Repurpose, Not priority  
**Opciones Q36**: Community, Announcements, Ads only, Light, None  
**Opciones Q38**: SEO, Education, Authority, Not sure

### Practice Suite & Growth (10 preguntas)
| ID | Pregunta | Tipo | Dependencia | Campo DB |
|----|----------|------|-------------|----------|
| Q39 | How would you like your Practice Suite managed? | Multiple Choice | - | `q39_suite_model` |
| Q40 | If a real person helped, what would you want? | Multi-Select | **Q39≠AI-only** | `q40_saya` |
| Q41 | Are you interested in SEO? | Multiple Choice | - | `q41_seo` |
| Q42 | Are you interested in Ads? | Multiple Choice | - | `q42_ads` |
| Q43 | What would success from growth look like? | Long Text | - | `q43_growth` |
| Q44 | If we could focus on ONE thing first? | Multiple Choice | - | `q44_priority` |
| Q45 | How fast do you want things to move? | Multiple Choice | - | `q45_pace` |
| Q46 | Anything that's burned you with past vendors? | Long Text | - | `q46_risk` |
| Q47 | What would feeling truly supported look like? | Long Text | - | `q47_success` |
| Q48 | Is there anything else you want us to know? | Long Text | - | `q48_notes` |

**Opciones Q39**: AI-run, Human support (upgrade), Mix, Not sure  
**Opciones Q40**: Inbox, Scheduling, Follow-ups, Admin, Projects  
**Opciones Q41/Q42**: Yes, Maybe later, No, Need guidance  
**Opciones Q44**: Systems, Support, Visibility, Content, Clarity  
**Opciones Q45**: Slow, Steady, Fast

---

## 🔀 PREGUNTAS CONDICIONALES

**Dependencias identificadas**:
1. **Q15** → Solo si Q14 = Yes (marketing company)
2. **Q30** → Solo si Q29 ≠ No (tiene website)
3. **Q31** → Solo si Q29 = No (no tiene website)
4. **Q33** → Solo si Q29 ≠ No (tiene website)
5. **Q35** → Solo si Instagram seleccionado en Q34
6. **Q36** → Solo si Facebook seleccionado en Q34
7. **Q37** → Solo si LinkedIn seleccionado en Q34
8. **Q38** → Solo si Blog seleccionado en Q34
9. **Q40** → Solo si Q39 ≠ AI-only (quiere ayuda humana)

---

## 📊 TIPOS DE CAMPO

| Tipo | Cantidad | Validador |
|------|----------|-----------|
| Short Text | 10 | `text` |
| Long Text | 15 | `long_text` |
| Multiple Choice | 15 | `choice` |
| Yes/No | 5 | `boolean` |
| Multi-Select | 2 | `multi_select` |
| Email | 1 | `email` |
| Scale | 1 | `scale` |

---

## 💾 CAMPOS ESPECIALES

### Campos Críticos (marcar en backend)
- **Q4**: EIN (campo seguro, encriptado)
- **Q11**: Point person (crítico para contacto)
- **Q39**: Suite model (define el servicio)

### Campos Opcionales
- **Q6**: Home address (solo si diferente)
- **Q8**: Texting line (solo si diferente de teléfono)

### Campos para Análisis
- **Q13**: Tech-savvy level (para personalizar soporte)
- **Q17**: Practice type (para segmentación)
- **Q44**: Priority (para roadmap del cliente)
- **Q45**: Pace (para expectativas de velocidad)

---

## ✅ PRÓXIMOS PASOS

1. **Backend**: Actualizar `workflow.py` para leer de `questions.json`
2. **Database**: Agregar campos JSONB por etapa
3. **Frontend**: Crear chat interface con progreso por etapas
4. **Validadores**: Implementar validadores para cada tipo
5. **GHL Integration**: Mapear 48 campos a custom fields

---

**Archivo de configuración**: `/backend/app/config/questions.json`  
**Última actualización**: 30 de diciembre de 2025
