# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


DEFAULT_TASKS = [
	'Contract, ID, KRA PIN & bank details on file',
	'Added to payroll, email & tools',
	'Read operations manual & relevant systems',
	'Position Contract & first-month goals agreed and signed',
	'Buddy/mentor assigned; equipment & access provided',
]


class Onboarding(Document):
	def before_insert(self):
		if not self.tasks:
			for t in DEFAULT_TASKS:
				self.append('tasks', {'task': t, 'done': 0})

	def validate(self):
		tasks = self.tasks or []
		done = len([t for t in tasks if t.done])
		self.completion = round(100.0 * done / len(tasks), 0) if tasks else 0
		if tasks and done == len(tasks):
			self.status = 'Completed'
