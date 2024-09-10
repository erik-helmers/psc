from django.db import models



class Sample(models.Model):


    sid = models.CharField(max_length=512, unique=True)
    name = models.CharField(max_length=512)
    path = models.CharField(max_length=4096, unique=True)
    signature = models.CharField(max_length=1024)

    def __str__(self):
        return self.sid



class Algo(models.Model):
    name = models.CharField(max_length=512)
    sid = models.CharField(max_length=512, unique=True)
    path = models.CharField(max_length=4096, unique=True)

    def __str__(self):
        return self.sid


class Hash(models.Model):

    value = models.TextField()
    algo = models.ForeignKey(Algo, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)


    class Meta:
        unique_together = [["algo", "sample"]]


    def __str__(self):
        return f"{self.algo.sid}/{self.sample.sid}"
