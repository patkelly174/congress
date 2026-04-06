import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from congress.tasks import bill_info, bills


class BillParsingRegressions(unittest.TestCase):
    def test_form_bill_json_dict_allows_missing_actions(self):
        xml_as_dict = {
            "billStatus": {
                "bill": {
                    "billType": "HR",
                    "billNumber": "10",
                    "congress": "119",
                    "titles": {"item": [{"titleType": "Official Title as Introduced", "title": "A bill."}]},
                    "sponsors": {
                        "item": [{
                            "fullName": "Rep. Doe, Jane [D-CA-12]",
                            "bioguideId": "D000001",
                            "state": "CA",
                            "district": "12",
                            "firstName": "JANE",
                            "lastName": "DOE",
                        }]
                    },
                    "subjects": {"billSubjects": {"legislativeSubjects": None}},
                    "summaries": {"billSummaries": {"item": []}},
                }
            }
        }

        bill_data = bills.form_bill_json_dict(xml_as_dict)

        self.assertEqual(bill_data["actions"], [])

    def test_sponsor_for_accepts_multi_letter_party_codes(self):
        sponsor = {
            "bioguideId": "L000304",
            "fullName": "Sen. Lieberman, Joseph I. [ID-CT]",
            "firstName": "JOSEPH",
            "lastName": "LIEBERMAN",
            "party": "ID",
            "state": "CT",
            "middleName": "I.",
        }

        parsed = bill_info.sponsor_for(sponsor)

        self.assertEqual(parsed["name"], "Lieberman, Joseph I.")
        self.assertEqual(parsed["state"], "CT")
        self.assertEqual(parsed["bioguide_id"], "L000304")

    def test_cosponsors_for_accepts_singleton_items(self):
        cosponsors = {
            "item": {
                "bioguideId": "L000304",
                "fullName": "Sen. Lieberman, Joseph I. [ID-CT]",
                "firstName": "JOSEPH",
                "lastName": "LIEBERMAN",
                "party": "ID",
                "state": "CT",
                "middleName": "I.",
                "sponsorshipDate": "2012-12-05",
                "isOriginalCosponsor": "True",
            }
        }

        parsed = bill_info.cosponsors_for(cosponsors)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["name"], "Lieberman, Joseph I.")
        self.assertTrue(parsed[0]["original_cosponsor"])


if __name__ == "__main__":
    unittest.main()
