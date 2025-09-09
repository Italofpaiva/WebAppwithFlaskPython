import os
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from jogoteca import app, db
from models import Jogos,Usuarios
from helpers import recupera_imagem, deleta_arquivo
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_logado' not in session or session['usuario_logado'] is None:
            return redirect(url_for('login', proxima=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    list = Jogos.query.order_by(Jogos.id)
    return render_template('listas.html', titulo='Jogos', jogos=list)


@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima= url_for('novo')))
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST'])
def criar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']

    jogo = Jogos.query.filter_by(nome=nome).first()
    if jogo:
        flash('Jogo já existente')
        return redirect(url_for('index'))

    novo_jogo = Jogos(nome=nome, categoria=categoria, console=console)
    db.session.add(novo_jogo)
    db.session.commit()

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    arquivo.save(os.path.join(upload_path, f'capa{novo_jogo.id}.jpg'))

    return redirect(url_for('index'))



@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima= url_for('novo')))
    jogo = Jogos.query.filter_by(id=id).first()
    capa_jogo = recupera_imagem(id)
    return render_template('editar.html', titulo='Editando jogo', jogo=jogo, capa_jogo=capa_jogo)

@app.route('/atualizar', methods=['POST'])
def atualizar():
   jogo = Jogos.query.filter_by(id=request.form['id']).first()
   jogo.nome = request.form['nome']
   jogo.categoria = request.form['categoria']
   jogo.console = request.form['console']

   db.session.add(jogo)
   db.session.commit()

   arquivo = request.files['arquivo']
   upload_path = app.config['UPLOAD_PATH']

   deleta_arquivo(jogo.id)
   arquivo.save(os.path.join(upload_path, f'capa{jogo.id}.jpg'))

   return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))

    Jogos.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Jogo deletado com sucesso')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST'])
def autenticar():
    nickname = request.form['nickname']
    senha = request.form['senha']

    usuario = Usuarios.query.filter_by(nickname=nickname).first()


    if usuario and  check_password_hash(usuario.senha, senha ):
        session['usuario_logado'] = usuario.nickname
        flash(usuario.nickname + ' logado sucesso!')
        proxima_pagina = request.form['proxima']
        return redirect(proxima_pagina)

    else:
        flash('Usuário não logado!')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
        session['usuario_logado'] = None
        flash('Logout feito com sucesso!')
        return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)

