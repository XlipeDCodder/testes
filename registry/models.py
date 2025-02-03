from django.db import models
from abc import ABC, abstractmethod
import re
import datetime

class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30)
    uf = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.nome}"

    def set_nome(self, nome: str):
        self.nome = nome
    
    def get_nome(self):
        return self.nome
    
    def set_uf(self, uf: str):
        self.uf = uf
    
    def get_uf(self):
        return self.uf
    

class Cidade(models.Model):
    id_cidade = models.AutoField(primary_key=True)
    estado = models.OneToOneField(Estado, on_delete=models.CASCADE, related_name="cidade")
    nome = models.CharField(max_length=60)
    cod_ibge = models.IntegerField

    def __str__(self):
        return f"{self.nome} - {self.estado.nome}"
    
    def validar_estado(self, estado: Estado):
        if not isinstance(estado, Estado) or not estado or Cidade.objects.filter(nome=self.nome, estado=estado).exists():
            raise ValueError
        return True
    
    def set_estado(self, estado: Estado):
        if self.validar_estado(estado) is True:
            self.estado = estado
    
    def get_estado(self):
        return self.estado
    
    def set_nome(self, nome: str):
        self.nome = nome
    
    def get_nome(self):
        return self.nome
    
    def set_cod_ibge(self, cod_ibge: int):
        self.cod_ibge = cod_ibge
    
    def get_cod_ibge(self):
        return self.cod_ibge


class Contato(models.Model):
    id_contato = models.AutoField(primary_key=True)
    contato_escolhas = [
        ("telefone", "Telefone"),
        ("email", "Email")
    ]
    tipo = models.CharField(max_length=10, choices=contato_escolhas)
    chave = models.CharField(max_length=25, null=False, blank=False)

    def __str__(self):
        return f"{self.chave}"


class Adress(models.Model):
    id_adress = models.AutoField(primary_key=True)
    adress_escolhas = [
        ("residencial", "Residencial"),
        ("fiscal", "Fiscal"),
        ("comercial", "Comercial")
    ]
    tipo = models.CharField(max_length=20, choices=adress_escolhas, default="residencial")
    logradouro = models.CharField(max_length=255)
    bairro = models.CharField(max_length=50) # Não sei se deixar ou não
    numero = models.CharField(max_length=10)
    cep = models.CharField(max_length=20)
    cidade = models.OneToOneField(Cidade, on_delete=models.CASCADE, related_name="adress")

    def __str__(self):
        return f"{self.logradouro}, {self.numero}, {self.bairro}, {self.cidade.nome}"


class Pessoa(models.Model, ABC):
    id_pessoa = models.AutoField(primary_key=True)
    contato = models.ManyToManyField(Contato, related_name="pessoa")
    adress = models.ManyToManyField(Adress, related_name="pessoa")
    data_cadastro = models.DateField(auto_now_add=True)

    @abstractmethod
    def validar_doc(self):
        pass
    
    def validar_contato(self, contato: Contato):
        if not isinstance(contato, Contato) or contato.tipo not in ["telefone", "email"] or self.contato.filter(chave=contato.chave).exists():
            raise ValueError
        if contato.tipo == "telefone":
            if not re.fullmatch(r'\d{9,15}', contato.chave):
                raise ValueError
        elif contato.tipo == "email":
            if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', contato.chave):
                raise ValueError
        return True

    def set_contato(self, contato: Contato):
        if self.validar_contato(contato) is True:
            self.contato.add(contato)
    
    def get_contato(self):
        return self.contato.all

    def validar_adress(self, adress: Adress):
        if not isinstance(adress, Adress) or self.adress.filter(logradouro=adress.logradouro, numero=adress.numero).exists() or not re.fullmatch(r'\d{5}-\d{3}|\d{8}', adress.cep):
            raise ValueError
        if not (adress.logradouro.strip() and adress.numero.strip() and adress.cep.strip()):
            raise ValueError
        return True
    
    def set_adress(self, adress: Adress):
        if self.validar_adress(adress) is True:
            self.adress.add(adress)
    
    def get_adress(self):
        return self.adress.all
    
    def set_data_cadastro(self):
        self.data_cadastro = datetime.datetime.now().strftime("%x")
    
    def get_data_cadastro(self):
        return self.data_cadastro

class Fisica(models.Model, Pessoa):
    pass

class Juridica(models.Model, Pessoa):
    pass
