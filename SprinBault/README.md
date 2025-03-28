Proyecto:

Descripción:
Aplicación web construida con FastAPI, MySQL y Python, diseñada para gestionar dispositivos de hardware y usuarios, incluyendo contraseñas maestras encriptadas para dispositivos.

La aplicación interactúa con dos bases de datos:
-- MonederoPW: Guarda los dispositivos de hardware, sus contraseñas encriptadas, y sus tipos.

-- SprindeUserAuthDatabase: Guarda los usuarios, contraseñas y roles (administrador o no).





La página principal de la aplicación ofrece 3 botones para acceder a diferentes secciones:
-- Usuarios: Para gestionar usuarios (insertar, modificar, eliminar).

-- Hardware: Para gestionar dispositivos de hardware (insertar, modificar, eliminar).

-- Tipos de Hardware: Para gestionar tipos de hardware (insertar, modificar, eliminar).


En cada página, se muestran los datos de las bases de datos en tablas, donde se pueden realizar las operaciones mencionadas.





NOTA: Existen dos archivos importantes para la gestión de contraseñas maestras y la encriptación de las contraseñas de hardware (insert_normal.py y insert_secret.py). Estos archivos contienen claves sensibles, por lo que se recomienda eliminarlos o guardarlos fuera del proyecto una vez que se haya completado la configuración.





Requisitos:
Antes de comenzar con la instalación, asegúrate de tener Python 3.9+ y MySQL instalados en tu máquina.


Instalar dependencias:
-- Para instalar las dependencias necesarias del proyecto, ejecuta el siguiente comando en tu terminal:

pip install -r requirements.txt

Este comando instalará todas las dependencias que están listadas en el archivo requirements.txt.


Generar el archivo requirements.txt:
-- Si necesitas generar el archivo requirements.txt (por ejemplo, después de haber instalado nuevas dependencias), puedes usar el siguiente comando:

pip freeze > requirements.txt


Uso:
-- Ejecuta el servidor de desarrollo: Para iniciar la aplicación, usa el siguiente comando:

uvicorn main:app --reload





Seguridad:
-- Contraseñas de hardware: Las contraseñas de hardware se encriptan usando una clave de encriptación especificada por el usuario.

-- Contraseña maestra: Solo los usuarios que conozcan la contraseña maestra podrán ver las contraseñas de los dispositivos.