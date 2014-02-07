#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MySQLdb
import md5

class DataBase():

	def __init__(self, host, user, passwd):
		self.host = host
		self.user = user
		self.passwd = passwd

	#cria conexão com banco de dados
	def createConnection(self):
		try: 
			dbConnection = MySQLdb.connect(self.host, self.user, self.passwd)
		except:
			print "Erro ao conectar com o Banco de Dados"
		return dbConnection

	#cria cursor
	def createCursor(self, dbConnection):
		dbCursor = dbConnection.cursor()
		return dbCursor

	#cria banco de dados, com a tabela users
	def createDB(self, dbConnection, dbCursor):
		try:
			dbConnection.select_db("ScriptBattle")
		except:
			dbCursor.execute("create database ScriptBattle")
			dbConnection.select_db("ScriptBattle")
			dbCursor.execute("create table users (id_usr int not null auto_increment, name varchar(15) not null, passwd varchar(32) not null, won integer, lost integer, primary key (id_usr));")	

	# cria população inicial para o banco de dados
	def populateDB(self, dbConnection, dbCursor):
		md5hash = md5.new()

		i = 0
		for i in range(3):
			name = raw_input("Please enter a name: ")
			password = raw_input("Please enter a password: ")

			md5hash.update(password)
			encPassword = md5hash.hexdigest()
			dbCursor.execute("insert into users (name, passwd) values (%s, %s)", (name, encPassword))

		dbConnection.commit()


if __name__ == "__main__":
	db = DataBase("localhost", "root", "v123")
	dbConnection = db.createConnection()
	try:
		dbConnection.select_db("ScriptBattle")
		dbCursor = db.createCursor(dbConnection)
	except:
		dbCursor = db.createCursor(dbConnection)
		db.createDB(dbConnection, dbCursor)
		db.populateDB(dbConnection, dbCursor)
	
	dbCursor.execute("select name,passwd from users order by name")
	resultSet = dbCursor.fetchall()

	print "Nome -- Senha (criptografada)"
	for results in resultSet:
		print results[0], "--", results[1]