

from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL 
import MySQLdb.cursors 
import re 
import json
from datetime import time


app = Flask(__name__) 


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'storedata'

mysql = MySQL(app) 

@app.route('/') 
@app.route('/login', methods =['GET', 'POST']) 
def login(): 
    msg = '' 
    if request.method == 'POST'  and 'password' in request.form: 
    
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM accounts WHERE  password = % s', ( password, )) 
        account = cursor.fetchone() 
        if account: 
            session['loggedin'] = True
        
            session['password'] = account['password'] 
            msg = 'Logged in successfully !'
            return render_template('home.html', msg = msg) 
        else: 
            msg = 'Incorrect  password !'
    return render_template('login.html', msg = msg) 

@app.route('/logout') 
def logout(): 
    session.pop('loggedin', None) 
    return redirect(url_for('login')) 

@app.route('/register', methods =['GET', 'POST']) 
def register(): 
    msg = '' 
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form : 
        email = request.form['email'] 
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM accounts where email = % s', (email, )) 
        account = cursor.fetchone() 
        if account: 
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'Invalid email address !'

        elif  not password or not email: 
            msg = 'Please fill out the form !'
        else: 
            cursor.execute('INSERT INTO accounts VALUES ( % s, % s)', ( email, password, )) 
            mysql.connection.commit() 
            msg = 'You have successfully registered !'
    elif request.method == 'POST': 
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg) 



@app.route('/product', methods =['GET', 'POST'])
def insert():
    msg=''
    if request.method =="POST":
        pid=request.form['pid']
        name=request.form['name']
        company=request.form['company']
        price=request.form['price']
        quantity=request.form['quantity']
        b=int(quantity)
    
        cursor = mysql.connection.cursor() 
        cursor.execute('SELECT quantity FROM products where id = % s ', (pid,)) 
        quan = cursor.fetchone()
        if quan:
            a=list(quan)
            msg="Product already exists! Update is successful!"
            cursor.execute("""UPDATE products SET quantity=%s WHERE id=%s""", (b+a[0],pid,))
            mysql.connection.commit()
        else:
            msg='Insertion of new product  is successful'
            
            cursor.execute('insert into products(id, name, company, price, quantity) values(%s, %s, %s, %s, %s)',(pid, name, company, price, quantity))
            mysql.connection.commit()
    return render_template('product.html',msg=msg)
        


@app.route('/buy', methods =['GET', 'POST'])
def buy():
    msg=''
    msg1=''
    if request.method =="POST":
        pid=request.form['pid']
        name=request.form['name']
        company=request.form['company']
        price=request.form['price']
        quantity=request.form['quantity']
        b=int(quantity)
        m=int(price)
       
        cursor = mysql.connection.cursor() 
        cursor.execute('SELECT quantity FROM products where id = % s', (pid, )) 
        quan = cursor.fetchone()
        if quan:
            a=list(quan)
            
            
            if a[0]>=b:
                msg="Product is bought successfully!"
                cursor.execute("""UPDATE products SET quantity=%s WHERE id=%s""", (a[0]-b,pid,))
                mysql.connection.commit()
                cursor.execute("select count(%s) from sold where id=%s",(pid,pid,))
                m=cursor.fetchone()
                om=list(m)
                if om[0]==0:
                    cursor.execute("""insert into sold(id,name,company,price,quantity) values(%s, %s, %s, %s, %s)""",(pid, name, company, price, quantity,))
                    mysql.connection.commit()
                else:
                    cursor.execute('SELECT quantity FROM sold where id = %s ', (pid,))
                    quan2=cursor.fetchone()
                    if quan2:
                        y=list(quan2)
                        cursor.execute('UPDATE sold SET quantity=%s WHERE id=%s', (y[0]+b,pid,))
                        mysql.connection.commit()


                cursor.execute('SELECT quantity FROM products where id = % s', (pid, )) 
                quans = cursor.fetchone()
                c=list(quans)
                if c[0] == 0:
                    flash("ALERT!Product is empty in the store! Do refill it")
                    return render_template('sales.html',msg=msg)
                mysql.connection.commit()
            else:
                
                msg=("Insufficient quantity..!Quantity available:")
                msg1=(a[0])
                
              
                

        else:
            msg="No such product in store"
    return render_template('sales.html',msg=msg,msg1=msg1)
    




@app.route('/check',methods =['GET', 'POST']) 
def check():
    
    if request.method =="POST":
        name=request.form['name']
        company=request.form['company']
        price=request.form['price']

        quan=int(price)
        cursor = mysql.connection.cursor()
        cursor.execute('select * from products where name=%s and company=%s and price<=%s', ( name,company,quan, )) 
        record=cursor.fetchall()
        if record:
            flash("Succesful!There are required products in stock!!")
            return render_template('check.html',value=record,)
        else:
            
            cursor = mysql.connection.cursor()
            cursor.execute('insert into demand  values(%s,%s,%s)', ( name,company,quan))
            mysql.connection.commit()
            cursor.execute('select * from products where name=%s and price<=%s', ( name,quan, )) 
            record=cursor.fetchall()

            if record:
                flash("Search not found! Look for same product of other companies..")
                return render_template('check2.html',value=record)
            else:
                flash("Oops! No results found! Please check for other similar products...")
                cursor = mysql.connection.cursor()
                cursor.execute('select id from products where name=%s and company=%s', ( name,company, )) 
                abc=cursor.fetchone()
                if abc:
                    p=list(abc)
                    cursor.execute('select substring(%s,1,2)',(p,))
                    pq=cursor.fetchone()
                    m=list(pq)
      
                    sc=m[0]
                    n=sc+"%"
           
                    cursor.execute('select * from products where not name=%s and price<=%s and id like %s ',(name,quan,n,))
                    data2 = cursor.fetchall()
                    return render_template('check2.html',value=data2,)
                else:
                    flash("Sorry! No similar products found too :(")
                    return render_template('check2.html')
               


                








       
    
@app.route('/loginemp')
def loginemp():
    
    return render_template('loginemp.html')
     
    
        

           
    


@app.route('/graphnew')
def graphnew():
    
    return render_template('graphnew.html')






@app.route('/graph') 
def graph():
    cursor=mysql.connection.cursor()
    cursor.execute('select max(floor(salespercent)) from tabulars group by name')
    record=cursor.fetchall()
    print(record)
    m=list(record)
    cursor.execute('select name from tabulars')
    record2=cursor.fetchall()
    n=list(record2)

    
    return render_template('graph.html',value=m,value2=n)


@app.route('/category') 
def category(): 
    
    return render_template('category.html') 
   
    


@app.route('/complaints') 
def complaints():
    cursor = mysql.connection.cursor()
    cursor.execute("select * from feedbacks")
    data = cursor.fetchall()
    return render_template('complaints.html',value=data) 






@app.route('/home') 
def home(): 
    
    
    return render_template('home.html') 


@app.route('/product') 
def product(): 
    
    return render_template('product.html') 


@app.route('/sales') 
def sales(): 
    
    return render_template('sales.html') 



@app.route('/feedback', methods =['GET', 'POST']) 
def feedback(): 

    msg=''
    if request.method =="POST":
        name=request.form['name']
        company=request.form['company']
        complaints=request.form['complaints']
       
        cursor = mysql.connection.cursor() 
        cursor.execute("""insert into feedbacks(name,company,complaints) values(%s, %s, %s)""",( name, company, complaints,))
        msg="Thank you for your review :)"
        mysql.connection.commit()

    
    return render_template('feedback.html',msg=msg) 


@app.route('/tabular') 
def tabular():
    cursor = mysql.connection.cursor()
    cursor.execute('select * from tabulars') 
    record=cursor.fetchall()
    return render_template('tabular.html',value=record) 


@app.route('/delete')
def deleteall():
    cursor=mysql.connection.cursor()
    cursor.execute('delete from feedbacks')
    mysql.connection.commit()
    flash("deleted successfully")
    return render_template('feedback.html')


@app.route('/analysis') 
def analysis(): 
    
    return render_template('analysis.html') 





@app.route('/homeapp') 
def ha():
    cursor = mysql.connection.cursor()
    strs="HA%"
    cursor.execute("select * from products where id like %s",(strs,))
    data = cursor.fetchall()
    return render_template('homeapp.html',value=data) 


@app.route('/electronic') 
def electronic(): 
    cursor = mysql.connection.cursor()
    strs="ED%"
    cursor.execute("select * from products where id like %s",(strs,))
    data = cursor.fetchall()
    return render_template('electronicdevice.html',value=data) 


@app.route('/Kitchen') 
def kitchen(): 
    cursor = mysql.connection.cursor()
    strs="KA%"
    cursor.execute("select * from products where id like %s",(strs,))
    data = cursor.fetchall()
    return render_template('kitchenapplainces.html',value=data) 





@app.route('/funiture') 
def furniture(): 
    cursor = mysql.connection.cursor()
    strs="FA%"
    cursor.execute("select * from products where id like %s",(strs,))
    data = cursor.fetchall()
    return render_template('furniture.html',value=data)
    
  

@app.route('/beauty') 
def la(): 
    cursor = mysql.connection.cursor()
    strs="BP%"
    cursor.execute("select * from products where id like %s",(strs,))
    data = cursor.fetchall()
    return render_template('beautyproduct.html',value=data)
    
    


@app.route('/bags') 
def ma(): 
    cursor = mysql.connection.cursor()
    strs="BA%"
    cursor.execute("select * from products where id like %s",(strs,))
    data = cursor.fetchall()
    return render_template('bags.html',value=data)


@app.route('/demand') 
def demand(): 
    cursor = mysql.connection.cursor()
   
    cursor.execute("select * from demand")
    data = cursor.fetchall()
    return render_template('demand.html',value=data)
    
   













if (__name__)=='__main__':
    app.run(debug=True)
