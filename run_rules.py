import psycopg2
from os import listdir
from os.path import splitext
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import csv

def run_rules(job_id, schema_name):
	meta_conn = psycopg2.connect("dbname='validator' user='testUser' host='localhost' password='testPwd'")
	meta_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	meta_c = meta_conn.cursor()
	meta_c.execute('UPDATE jobs SET status=\'starting_rules\' WHERE job_id=%d' % job_id)
	conn = psycopg2.connect("dbname='job_%d' user='testUser' host='localhost' password='testPwd'" % job_id)
	c = conn.cursor()

	reader = csv.reader(open('rules/%s.csv' % schema_name, 'rb'), quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
	header = reader.next()

	for row in reader:
		sql = row[header.index('sql')]
		print "Running rule %s: %s" % (row[header.index('id')], sql)
		c.execute(sql)
		invalid_count = 0
		for row in c.fetchall():
			invalid_count += 1
		print '==> Found %d invalid rows.' % invalid_count
	conn.close()
	meta_c.execute("UPDATE jobs SET status='finished_rules' WHERE job_id=%d" % job_id)
	meta_conn.close()