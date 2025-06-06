from config.conexion import conexion
from flask import Flask, render_template,request,redirect,session,make_response
from fpdf import FPDF

app = Flask(__name__)


app.secret_key='MiClave'

def mostrarTodo():
    cursor = conexion.cursor()
    cursor.execute('select * from tbcliente')
    clientes = cursor.fetchall()
    cursor.close()
    return clientes


@app.route('/insertar', methods=['POST'])
def insertar():
    nombre=request.form['txtnombre']
    nit=request.form['txtnit']
    cursor = conexion.cursor()
    sql="INSERT INTO tbcliente (nombre, nit) VALUES (%s, %s)"
    cursor.execute(sql, (nombre , nit))
    conexion.commit()
    cursor.close()
    clientes=mostrarTodo()
    mensaje="Registro insertado correctamente"
    return render_template ('registrar.html',mensaje=mensaje,clientes=clientes)

@app.route('/')
def index():
    if 'usuario' in session:
        datos=mostrarTodo()
        return render_template('registrar.html', clientes=datos)
    return render_template("login.html")

@app.route('/actualizar/<id>')
def actualizar(id):
    cursor=conexion.cursor()
    sql="select * from tbcliente where ID_cliente=%s"
    cursor.execute(sql,(id,))
    dato=cursor.fetchone()
    cursor.close
    return render_template('actualizar.html' ,dato=dato)

@app.route('/actualizar_cliente', methods=['POST'])
def actualizar_cliente():
    id = request.form['id']
    nombre = request.form['nombre']
    nit = request.form['nit']
    cursor = conexion.cursor()
    sql = "UPDATE tbcliente SET nombre = %s, nit = %s WHERE ID_cliente = %s"
    cursor.execute(sql, (nombre, nit, id))
    conexion.commit()
    cursor.close()
    return redirect('/')

@app.route('/eliminar/<id>')
def eliminar(id):
    cursor=conexion.cursor()
    sql=("DELETE FROM tbcliente WHERE ID_cliente=%s")
    cursor.execute(sql,(id,))
    conexion.commit()
    cursor.close()
    return redirect('/')

@app.route('/comprar/<id>')
def comprar(id):
    datos=mostrarCliente(id)
    return render_template('comprar.html',id=id , datos=datos)


@app.route('/comprar', methods=['post'])
def insertarcompra():
    id=request.form['txtid']
    producto=request.form["txtproducto"]
    cantidad=request.form['txtcantidad']
    costo=request.form['txtcosto']
    print(f"ID recibido: {id}, Producto: {producto}, Cantidad: {cantidad}, Costo: {costo}")

    cursor=conexion.cursor()
    sql="INSERT INTO tbcompra(producto,cantidad,costo,tbcliente_id_cliente) values(%s, %s,%s, %s)"
    cursor.execute(sql,(producto,cantidad,costo,id))
    conexion.commit()
    cursor.close
    mostrar=mostrarTodo()
    return render_template('registrar.html',mostrar=mostrar)


def mostrarCliente(id):
    cursor=conexion.cursor()
    sql="SELECT * FROM tbcliente WHERE ID_cliente=%s"
    cursor.execute(sql,(id,))
    dato=cursor.fetchone()
    return dato

@app.route('/login', methods=['GET','POST'])
def login():
    mensaje=''
    if request.method=='POST':
        user=request.form['txtuser']
        clave=request.form['txtclave']

        cursor=conexion.cursor()
        sql='Select * from tbusuario where user=%s AND clave =%s'
        cursor.execute(sql,(user,clave))
        usuario=cursor.fetchone()
        cursor.close()

        if usuario:
            session['usuario']=usuario[1]
            session['clave']=usuario[3]
            return redirect('/')
        else:
            mensaje="Usuario o contraseña incorrecto"
    return render_template('login.html',mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/buscar',methods=['GET'])
def buscar():
    buscar=request.args.get('txtbuscar')
    cursor=conexion.cursor()
    sql="SELECT * FROM tbcliente WHERE nombre LIKE %s"
    #Buscas nombre que terminen por la letra buscada
    cursor.execute(sql,(buscar+'%',))
   
    #Buscas nombre que contengan por la letra buscada
    #cursor.execute(sql,('%'+buscar+'%',))
    datos=cursor.fetchall()
    return render_template('registrar.html', clientes=datos)

@app.route('/vercompras/<id>', methods=['get'])
def vercompras(id):
    cursor=conexion.cursor()
    sql="select * from tbcompra where id_compra=%s"
    cursor.execute(sql,(id,))
    datos=cursor.fetchall()
    return render_template('vercompras.html',datos=datos)



@app.route('/reporte/<id>')
def generar_pdf(id):
    cursor = conexion.cursor()

    sql = """
    SELECT c.nombre, c.nit, co.producto, co.cantidad, co.costo
    FROM tbcompra co
    INNER JOIN tbcliente c ON co.ID_cliente = c.ID_cliente
    WHERE co.ID_cliente = %s
    """
    cursor.execute(sql, (id,))
    datos = cursor.fetchall()
    cursor.close()

    if not datos:
        return "No se encontraron compras para este cliente", 404

    nombre_cliente = datos[0][0]  # El nombre viene en la primera columna
    nit_cliente = datos[0][1]  # El NIT viene en la

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="REPORTE DE COMPRAS", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Cliente: {nombre_cliente}", ln=True)
    pdf.cell(200, 5, txt=f"NIT: {nit_cliente}", ln=True)
    pdf.ln(5)

    # Cabecera de la tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Producto", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.cell(30, 10, "Costo", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    # Datos
    pdf.set_font("Arial", '', 10)
    for fila in datos:
        _, _, producto, cantidad, costo = fila
        total = float(cantidad) * float(costo)
        pdf.cell(60, 10, str(producto), 1)
        pdf.cell(30, 10, str(cantidad), 1)
        pdf.cell(30, 10, f"{costo:.2f}", 1)
        pdf.cell(40, 10, f"{total:.2f}", 1)
        pdf.ln()

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_compras.pdf'
    return response
    

if __name__ == '__main__':

    app.run(debug=True)




   