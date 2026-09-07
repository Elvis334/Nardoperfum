from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, admin_required
from datetime import datetime

from cs50 import SQL




app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

#Database setup
db = SQL("sqlite:///database.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




@app.route("/")
def inicio():
    print("ruta /")
    peliculas = db.execute("SELECT * FROM peliculas")
    for pelicula in peliculas:
        print(pelicula)
    return render_template("index.html", peliculas=peliculas)


@app.route("/funcion/<id>")
def funcion_pelicula(id):
    funciones = db.execute("SELECT * FROM funciones  WHERE pelicula_id = ?", id)
    pelicula = db.execute("SELECT * FROM peliculas where pelicula_id = ?", id)[0]
    for funcion in funciones:
        print(funcion)

    return render_template("funciones.html",funciones=funciones, pelicula=pelicula)
    #return(f"aqui van a salir las funciones de la pelicula con id: {id}")


@app.route("/comprar/funcion/<id>", methods=["GET", "POST"])
@login_required
def comprar_funcion(id):
    funcion = db.execute("SELECT * FROM funciones INNER JOIN peliculas ON (funciones.pelicula_id = peliculas.pelicula_id) WHERE funcion_id = ?", id)[0]
    print(funcion)

    if request.method == "POST" :
        usuario = session["user_id"]
        entradas = request.form.get("entradas")
        entradas = int(entradas)

        print(entradas)
        print(usuario, "@@@@@@")
        fecha = datetime.now()
        for i in range(entradas):
            db.execute("INSERT INTO funcion_usuario (funcion_id, fecha, usuario_id) VALUES (?, ?, ?)", id, fecha, usuario)

    return render_template("pago.html", funcion=funcion)
#{%for pelicula in peliculas%}

#{%endfor%}


@app.route("/registro", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        cedula = request.form.get("cedula")
        passtext = request.form.get("password")

        print(username, email, cedula, passtext)

        if not request.form.get("username"):
            return "Introduzca un nombre de usuario"

        if not request.form.get("email"):
            return "Introduzca un correo electronico"

        if not request.form.get("cedula"):
            return "Introduzca un numero de cedula"

        if not request.form.get("password"):
            return "Introduzca una contraseña"

        correo = db.execute("SELECT * FROM usuarios WHERE correo = ? ", email)
        user = db.execute("SELECT * FROM usuarios WHERE username = ?", username)

        if len (correo) > 0:
            return("Este correo ya esta siendo utilizado")

        if len (user) > 0:
            return ("Este Usuario ya esta siendo utilizado")


        db.execute("INSERT INTO usuarios (username, cedula, correo, hash ) VALUES (?, ?, ?, ?)", username, cedula, email, generate_password_hash(passtext))
        redirect("/iniciar-sesion")







    return render_template("usuario-registro.html")


@app.route("/iniciar-sesion", methods=["GET", "POST"])
def registrar_usuario():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        consulta = db.execute("SELECT * FROM usuarios WHERE username = ?", username)

        if len(consulta) == 0:
            return ("Usuario o contraseña incorrecta")

        if not check_password_hash(consulta[0]["hash"], password):
            return "Usuario o contraseña incorrecta"

        session["user_id"] = consulta[0]["usuario_id"]
        return redirect("/")



    return render_template("usuario-inicio-session.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("login-admin.html")

        elif request.form.get("username") and request.form.get("password"):

            consult_admin = db.execute("SELECT * FROM admin WHERE username = ?", request.form.get("username"))

            if len(consult_admin) != 1 or not check_password_hash(
                consult_admin[0]["hash"], request.form.get("password")
            ):
                return render_template("login-admin.html")

            session["admin_id"] = consult_admin[0]["admin_id"]

            return redirect ("/admin/peliculas")

    else:

        return(render_template("login-admin.html"))


@app.route("/admin/peliculas", methods=["GET", "POST"])
@admin_required
def admin_peliculas():
    peliculas = db.execute("SELECT * FROM peliculas")
    funciones = db.execute("SELECT * FROM funciones INNER JOIN peliculas ON(funciones.pelicula_id = peliculas.pelicula_id)")

    for p in peliculas:
        print(p)

    return render_template("peliculas-admin.html", peliculas=peliculas, funciones=funciones)

@app.route("/admin/agregar-peliculas", methods = ["GET", "POST"])
@admin_required
def admin_agregar():
    if request.method == "POST":
        if not request.form.get("nombre") or not request.form.get("duracion") or not request.form.get("fecha_inicio") or not request.form.get("fecha_fin") or not request.form.get("sinopsis"):
            return("Error, introduzca todos los datos")


        nombre = request.form.get("nombre")
        duracion =  request.form.get("duracion")
        fecha_in =  request.form.get("fecha_inicio")
        fecha_out =  request.form.get("fecha_fin")
        sinopsis =  request.form.get("sinopsis")
        imagen = request.form.get("imagen")

        db.execute("INSERT INTO peliculas (nombre, sinopsis, duracion, fecha_inicio, fecha_fin, imagen) VALUES(?, ?, ?, ?, ?, ?) ", nombre, sinopsis, duracion, fecha_in, fecha_out, imagen)

    return render_template("agregar-admin.html")

@app.route("/admin/editar-peliculas/<int:id>", methods = ["GET", "POST"] )
@admin_required
def editar_pelicula(id):

    pelicula = db.execute("SELECT * FROM peliculas WHERE pelicula_id = ?", id)[0]
    print(pelicula)

    if request.method == "POST":
        if not request.form.get("nombre") or not request.form.get("duracion") or not request.form.get("fecha_inicio") or not request.form.get("fecha_fin") or not request.form.get("sinopsis"):
            return("Error, introduzca todos los datos")

        nombre = request.form.get("nombre")
        duracion =  request.form.get("duracion")
        fecha_in =  request.form.get("fecha_inicio")
        fecha_out =  request.form.get("fecha_fin")
        sinopsis =  request.form.get("sinopsis")
        imagen = request.form.get("imagen")

        print(imagen)

        print(db.execute(f"UPDATE peliculas SET nombre = ?, duracion = ?, fecha_inicio = ?, fecha_fin = ?, sinopsis = ?, imagen = ?   WHERE pelicula_id = ?", nombre,duracion,fecha_in,fecha_out,sinopsis,imagen, id))
        return redirect("/admin/peliculas")

    else:
        return render_template("editar-pelicula.html", pelicula=pelicula)



@app.route("/admin/agregar-funciones", methods = ["GET", "POST"])
@admin_required
def admin_funciones ():

    peliculas = db.execute("SELECT * FROM peliculas order by fecha_inicio ASC")
    salas = db.execute("SELECT * FROM salas")
    if request.method == "POST":
        if not request.form.get("pelicula") or not request.form.get("sala") or not request.form.get("hora_inicio") or not request.form.get("hora_fin") or not request.form.get("precio"):
            return("Error, introduzca todos los datos")

        pelicula = request.form.get("pelicula")
        sala = request.form.get("sala")
        if pelicula == "Seleccione Pelicula":
            return("Pelicula Incorrecta")
        if sala == "Seleccione Sala":
            return("Sala Incorrecta")

        hora_init = request.form.get("hora_inicio")
        hora_finish = request.form.get("hora_fin")
        price = request.form.get("precio")

        db.execute("INSERT INTO funciones(pelicula_id, sala_id, hora_inicio, hora_fin, precio) VALUES(?,?,?,?,?)", pelicula, sala, hora_init, hora_finish, price)

    return render_template("funcion-admin.html", peliculas=peliculas, salas=salas)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/iniciar-sesion")


if __name__ == "__main__":
    app.run(debug=True)
