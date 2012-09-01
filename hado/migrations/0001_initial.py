# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'User'
        db.create_table('hado_user', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('profile_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('utype', self.gf('django.db.models.fields.CharField')(default='MEM', max_length=3)),
        ))
        db.send_create_signal('hado', ['User'])

        # Adding model 'ContractType'
        db.create_table('hado_contracttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
        ))
        db.send_create_signal('hado', ['ContractType'])

        # Adding model 'Contract'
        db.create_table('hado_contract', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('valid_till', self.gf('django.db.models.fields.DateField')()),
            ('ctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hado.ContractType'], null=True)),
            ('tier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hado.Tier'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contracts', null=True, to=orm['hado.User'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal('hado', ['Contract'])

        # Adding model 'Tier'
        db.create_table('hado_tier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fee', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hado.ContractType'], null=True)),
        ))
        db.send_create_signal('hado', ['Tier'])

        # Adding model 'Payment'
        db.create_table('hado_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_paid', self.gf('django.db.models.fields.DateField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('method', self.gf('django.db.models.fields.CharField')(default='EFT', max_length=3)),
            ('contract', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', null=True, to=orm['hado.Contract'])),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments_made', null=True, to=orm['hado.User'])),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('hado', ['Payment'])

        # Adding model 'Locker'
        db.create_table('hado_locker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locker', null=True, to=orm['hado.User'])),
            ('num', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('hado', ['Locker'])


    def backwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('hado_user')

        # Deleting model 'ContractType'
        db.delete_table('hado_contracttype')

        # Deleting model 'Contract'
        db.delete_table('hado_contract')

        # Deleting model 'Tier'
        db.delete_table('hado_tier')

        # Deleting model 'Payment'
        db.delete_table('hado_payment')

        # Deleting model 'Locker'
        db.delete_table('hado_locker')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hado.contract': {
            'Meta': {'object_name': 'Contract'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hado.ContractType']", 'null': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'tier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hado.Tier']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contracts'", 'null': 'True', 'to': "orm['hado.User']"}),
            'valid_till': ('django.db.models.fields.DateField', [], {})
        },
        'hado.contracttype': {
            'Meta': {'object_name': 'ContractType'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hado.locker': {
            'Meta': {'object_name': 'Locker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locker'", 'null': 'True', 'to': "orm['hado.User']"})
        },
        'hado.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'null': 'True', 'to': "orm['hado.Contract']"}),
            'date_paid': ('django.db.models.fields.DateField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'default': "'EFT'", 'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments_made'", 'null': 'True', 'to': "orm['hado.User']"}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'hado.tier': {
            'Meta': {'object_name': 'Tier'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hado.ContractType']", 'null': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fee': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hado.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['auth.User']},
            'profile_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'utype': ('django.db.models.fields.CharField', [], {'default': "'MEM'", 'max_length': '3'})
        }
    }

    complete_apps = ['hado']
