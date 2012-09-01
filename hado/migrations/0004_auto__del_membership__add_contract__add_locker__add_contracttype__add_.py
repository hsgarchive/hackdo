# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting model 'Membership'
        db.delete_table('hado_membership')

        # Adding model 'Contract'
        db.create_table('hado_contract', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('ctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hado.ContractType'], null=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='memberships', null=True, to=orm['hado.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hado', ['Contract'])

        # Adding model 'Locker'
        db.create_table('hado_locker', (
            ('num', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locker', null=True, to=orm['hado.User'])),
        ))
        db.send_create_signal('hado', ['Locker'])

        # Adding model 'ContractType'
        db.create_table('hado_contracttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
        ))
        db.send_create_signal('hado', ['ContractType'])

        # Adding field 'User.utype'
        db.add_column('hado_user', 'utype', self.gf('django.db.models.fields.CharField')(default='MEM', max_length=3), keep_default=False)

        # Deleting field 'Payment.category'
        db.delete_column('hado_payment', 'category')

        # Deleting field 'Payment.for_year'
        db.delete_column('hado_payment', 'for_year')

        # Deleting field 'Payment.membership'
        db.delete_column('hado_payment', 'membership_id')

        # Deleting field 'Payment.for_month'
        db.delete_column('hado_payment', 'for_month')

        # Adding field 'Payment.contract'
        db.add_column('hado_payment', 'contract', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', null=True, to=orm['hado.Contract']), keep_default=False)

        # Adding field 'Payment.amount'
        db.add_column('hado_payment', 'amount', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)

        # Changing field 'Payment.user'
        db.alter_column('hado_payment', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.User']))


    def backwards(self, orm):

        # Adding model 'Membership'
        db.create_table('hado_membership', (
            ('tier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hado.Tier'], null=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='memberships', null=True, to=orm['hado.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hado', ['Membership'])

        # Deleting model 'Contract'
        db.delete_table('hado_contract')

        # Deleting model 'Locker'
        db.delete_table('hado_locker')

        # Deleting model 'ContractType'
        db.delete_table('hado_contracttype')

        # Deleting field 'User.utype'
        db.delete_column('hado_user', 'utype')

        # Adding field 'Payment.category'
        db.add_column('hado_payment', 'category', self.gf('django.db.models.fields.CharField')(default='FEE', max_length=3), keep_default=False)

        # Adding field 'Payment.for_year'
        db.add_column('hado_payment', 'for_year', self.gf('django.db.models.fields.CharField')(default=2009, max_length=4), keep_default=False)

        # Adding field 'Payment.membership'
        db.add_column('hado_payment', 'membership', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='membership_payments', to=orm['hado.Membership']), keep_default=False)

        # Adding field 'Payment.for_month'
        db.add_column('hado_payment', 'for_month', self.gf('django.db.models.fields.CharField')(default=12, max_length=2), keep_default=False)

        # Deleting field 'Payment.contract'
        db.delete_column('hado_payment', 'contract_id')

        # Deleting field 'Payment.amount'
        db.delete_column('hado_payment', 'amount')

        # Changing field 'Payment.user'
        db.alter_column('hado_payment', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hado.User']))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hado.contract': {
            'Meta': {'object_name': 'Contract'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hado.ContractType']", 'null': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'null': 'True', 'to': "orm['hado.User']"})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments_made'", 'null': 'True', 'to': "orm['hado.User']"})
        },
        'hado.tier': {
            'Meta': {'object_name': 'Tier'},
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
