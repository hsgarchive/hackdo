# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'hado_user')

        # Adding model 'HackDoUser'
        db.create_table(u'hado_hackdouser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40, db_index=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255, db_index=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_hackdo_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('profile_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('utype', self.gf('django.db.models.fields.CharField')(default='MEM', max_length=3)),
        ))
        db.send_create_signal(u'hado', ['HackDoUser'])

        # Adding M2M table for field groups on 'HackDoUser'
        m2m_table_name = db.shorten_name(u'hado_hackdouser_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hackdouser', models.ForeignKey(orm[u'hado.hackdouser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['hackdouser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'HackDoUser'
        m2m_table_name = db.shorten_name(u'hado_hackdouser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hackdouser', models.ForeignKey(orm[u'hado.hackdouser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['hackdouser_id', 'permission_id'])


        # Changing field 'Contract.user'
        db.alter_column(u'hado_contract', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.HackDoUser']))

        # Changing field 'Locker.user'
        db.alter_column(u'hado_locker', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.HackDoUser']))

        # Changing field 'Payment.user'
        db.alter_column(u'hado_payment', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.HackDoUser']))

    def backwards(self, orm):
        # Adding model 'User'
        db.create_table(u'hado_user', (
            ('utype', self.gf('django.db.models.fields.CharField')(default='MEM', max_length=3)),
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('profile_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('hado', ['User'])

        # Deleting model 'HackDoUser'
        db.delete_table(u'hado_hackdouser')

        # Removing M2M table for field groups on 'HackDoUser'
        db.delete_table(db.shorten_name(u'hado_hackdouser_groups'))

        # Removing M2M table for field user_permissions on 'HackDoUser'
        db.delete_table(db.shorten_name(u'hado_hackdouser_user_permissions'))


        # Changing field 'Contract.user'
        db.alter_column(u'hado_contract', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.User']))

        # Changing field 'Locker.user'
        db.alter_column(u'hado_locker', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.User']))

        # Changing field 'Payment.user'
        db.alter_column(u'hado_payment', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['hado.User']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hado.contract': {
            'Meta': {'object_name': 'Contract'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hado.ContractType']", 'null': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'tier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hado.Tier']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contracts'", 'null': 'True', 'to': u"orm['hado.HackDoUser']"}),
            'valid_till': ('django.db.models.fields.DateField', [], {})
        },
        u'hado.contracttype': {
            'Meta': {'object_name': 'ContractType'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'hado.hackdouser': {
            'Meta': {'object_name': 'HackDoUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_hackdo_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'profile_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            'utype': ('django.db.models.fields.CharField', [], {'default': "'MEM'", 'max_length': '3'})
        },
        u'hado.locker': {
            'Meta': {'object_name': 'Locker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locker'", 'null': 'True', 'to': u"orm['hado.HackDoUser']"})
        },
        u'hado.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'null': 'True', 'to': u"orm['hado.Contract']"}),
            'date_paid': ('django.db.models.fields.DateField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'default': "'EFT'", 'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments_made'", 'null': 'True', 'to': u"orm['hado.HackDoUser']"}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'hado.tier': {
            'Meta': {'object_name': 'Tier'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hado.ContractType']", 'null': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fee': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['hado']