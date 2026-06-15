# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


DEFAULT_PHASES = [
	('Initiation', 'Project Charter signed; scope & success measures agreed'),
	('Planning', 'Configuration, data-migration & integration plan set'),
	('Build & Configure', 'Modules configured; integrations; demos'),
	('Train & Go-live', 'UAT, training, data migration, phased go-live'),
	('Support & Optimise', 'Hypercare, SLAs, monitoring, lessons learned'),
]


class OnboardingProject(Document):
	def before_insert(self):
		if not self.phases:
			for name, desc in DEFAULT_PHASES:
				self.append('phases', {'phase': name, 'description': desc, 'done': 0})

	def validate(self):
		phases = self.phases or []
		done = len([p for p in phases if p.done])
		self.progress = round(100.0 * done / len(phases), 0) if phases else 0
		if phases and done == len(phases):
			self.status = 'Live'
