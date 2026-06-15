# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


STAGE_PRELIM = 'Preliminary'
STAGE_TECH = 'Technical'
STAGE_FIN = 'Financial'


class BidEvaluation(Document):
	def validate(self):
		self.check_committee_coi()
		self.compute()

	def check_committee_coi(self):
		if not self.committee:
			return
		com = frappe.get_doc('Evaluation Committee', self.committee)
		for m in (com.members or []):
			if not m.coi_declared:
				frappe.throw('All committee members must submit a conflict-of-interest declaration.')
			if m.has_conflict:
				frappe.throw('A committee member has a declared conflict of interest and must be replaced.')

	def compute(self):
		# Group scores per bid and per stage
		bids = {}
		for s in (self.scores or []):
			s.weighted_score = (s.score or 0) * (s.weight or 0) / 100.0
			b = bids.setdefault(s.bid, {STAGE_PRELIM: [], STAGE_TECH: [], STAGE_FIN: []})
			b.setdefault(s.stage, []).append(s)
		results = []
		for bid, stages in bids.items():
			prelim_ok = all((x.score or 0) >= 1 for x in stages.get(STAGE_PRELIM, [])) \
				if stages.get(STAGE_PRELIM) else True
			tech = sum(x.weighted_score for x in stages.get(STAGE_TECH, []))
			fin = sum(x.weighted_score for x in stages.get(STAGE_FIN, []))
			tech_ok = tech >= (self.technical_pass_mark or 0)
			responsive = prelim_ok and tech_ok
			results.append({'bid': bid, 'tech': tech, 'fin': fin,
				'combined': tech + fin, 'responsive': responsive})
		responsive = [r for r in results if r['responsive']]
		ranked = sorted(responsive, key=lambda r: r['combined'], reverse=True)
		if ranked:
			best = ranked[0]
			self.recommended_bid = best['bid']
			self.recommended_supplier = frappe.db.get_value('Bid', best['bid'], 'supplier')
			lines = ['Evaluation results (responsive bids ranked by combined score):']
			for i, r in enumerate(ranked, 1):
				sup = frappe.db.get_value('Bid', r['bid'], 'supplier')
				lines.append('%d. %s - technical %.1f, financial %.1f, combined %.1f'
					% (i, sup, r['tech'], r['fin'], r['combined']))
			self.evaluation_summary = '\n'.join(lines)
		else:
			self.evaluation_summary = 'No responsive bids. Procurement should be re-advertised.'
