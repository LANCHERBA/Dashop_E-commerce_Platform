from django.db import models

class BaseModel(models.Model):
    #此类可为其他模型类补充字段　－　抽象类
    created_time = models.DateTimeField(auto_now_add=True,
                    verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True,
                    verbose_name='更新时间')

    class Meta:
        abstract  = True
