# 🚀 Comandos de Deployment para Railway

Una vez instalado Railway CLI, ejecuta estos comandos en orden:

## 1. Iniciar Sesión
```bash
railway login
```
Te abrirá el navegador para autenticarte con GitHub/Google

## 2. Inicializar Proyecto
```bash
railway init
```

## 3. Desplegar
```bash
railway up
```

## 4. Configurar Variables de Entorno
En Railway Dashboard → Variables → Add:

```
SECRET_KEY = tu_clave_secreta_muy_segura_aqui
RAILWAY_ENVIRONMENT = production
DB_PATH = /tmp/trading_system.db
```

## 5. Acceder a tu App
Railway te dará una URL como:
https://tu-proyecto.railway.app

## 🔧 Generar SECRET_KEY seguro:
```python
import secrets
print(secrets.token_hex(32))
```

## 📱 Tu Sistema de Trading incluirá:
✅ Login/Registro de usuarios
✅ Registro de trades (Boom/Crash)
✅ Estadísticas y análisis
✅ Estrategias de Machine Learning
✅ Cuadernos personales
✅ Tracking de hábitos
✅ Gestión de riesgo
✅ Gráficos en tiempo real
✅ Gamificación

¡Tu sistema estará completo en Railway! 🎉
