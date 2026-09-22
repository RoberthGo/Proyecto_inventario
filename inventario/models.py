from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver


class Color(models.Model):
    descripcion = models.CharField(max_length=50, unique=True, verbose_name="Descripción del Color")

    def __str__(self):
        return self.descripcion


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)   
    telefono = models.CharField(max_length=20, blank=True, default='')
    correo = models.EmailField(blank=True, default='')
    
    def __str__(self):
        return self.nombre


class Ropa(models.Model):
    class TallaChoices(models.TextChoices):
        UNITALLA = 'UNITALLA', 'Unitalla'
        EXTRA_CHICA = 'XS', 'Extra Chica'
        CHICA = 'S', 'Chica'
        MEDIANA = 'M', 'Mediana'
        GRANDE = 'L', 'Grande'
        EXTRA_GRANDE = 'XL', 'Extra Grande'

    class TipoChoices(models.TextChoices):
        PLAYERA = 'PLAYERA', 'Playera'
        PANTALON = 'PANTALON', 'Pantalón'
        SUDADERA = 'SUDADERA', 'Sudadera'
        CHAMARRA = 'CHAMARRA', 'Chamarra'
        OTRO = 'OTRO', 'Otro'

    modelo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, default='')

    tipo = models.CharField(
        max_length=20,
        choices=TipoChoices.choices,
        default=TipoChoices.PLAYERA
    )

    talla = models.CharField(
        max_length=10,
        choices=TallaChoices.choices,
        default=TallaChoices.UNITALLA
    )

    marca = models.CharField(max_length=100)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='prendas'
    )

    colores = models.ManyToManyField(
        Color,
        through='Inventario',
        related_name='prendas'
    )

    def __str__(self):
        return f"{self.modelo} ({self.get_talla_display()}) - {self.marca}"


class Inventario(models.Model):
    ropa = models.ForeignKey(
        Ropa,
        on_delete=models.CASCADE,
        related_name='inventarios'
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name='inventarios'
    )
    unidades = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ropa', 'color'],
                name='unique_ropa_color_inventario'
            )
        ]

    def __str__(self):
        return f"{self.ropa.modelo} - {self.color.descripcion}: {self.unidades} uds"


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ventas'
    )

    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    items = models.ManyToManyField(
        Inventario,
        through='DetalleVenta',
        related_name='ventas'
    )

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        related_name='detalles_venta'

    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.cantidad}x {self.inventario.ropa.modelo} ({self.inventario.color.descripcion}) - Venta #{self.venta_id}"
