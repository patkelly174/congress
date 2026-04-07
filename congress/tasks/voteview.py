# Downloads member ideology and party data from Voteview.com.
# Provides DW-NOMINATE scores and related data that supplements
# the roll call vote data collected by the votes task.
#
# Defaults to the current congress. Use --congress to override, or --all for every congress.
#
# usc-run voteview
# usc-run voteview --congress=119
# usc-run voteview --congress=118,119
# usc-run voteview --all

import csv
import io
import logging
import os

from congress.tasks import utils

MEMBERS_URL = "https://voteview.com/static/data/out/members/HSall_members.csv"
PARTIES_URL = "https://voteview.com/static/data/out/parties/HSall_parties.csv"


def run(options):
    congress_opt = options.get("congress", None)
    if options.get("all", False):
        congress_filter = None
    elif congress_opt:
        congress_filter = set(str(c) for c in str(congress_opt).split(","))
    else:
        congress_filter = {str(utils.current_congress())}

    logging.warn("Downloading member ideology data from Voteview...")
    members_csv = utils.download(MEMBERS_URL, "voteview/HSall_members.csv", options)
    if not members_csv:
        logging.error("Failed to download members CSV.")
        return None

    logging.warn("Downloading party ideology data from Voteview...")
    parties_csv = utils.download(PARTIES_URL, "voteview/HSall_parties.csv", options)
    if not parties_csv:
        logging.error("Failed to download parties CSV.")
        return None

    members_by_congress = {}
    for row in csv.DictReader(io.StringIO(members_csv)):
        congress = row["congress"]
        if congress_filter is not None and congress not in congress_filter:
            continue
        if row["chamber"] == "President":
            continue
        members_by_congress.setdefault(congress, []).append(parse_member(row))

    parties_by_congress = {}
    for row in csv.DictReader(io.StringIO(parties_csv)):
        congress = row["congress"]
        if congress_filter is not None and congress not in congress_filter:
            continue
        if row["chamber"] == "President":
            continue
        parties_by_congress.setdefault(congress, []).append(parse_party(row))

    all_congresses = set(list(members_by_congress.keys()) + list(parties_by_congress.keys()))
    for congress in sorted(all_congresses, key=int):
        output_dir = os.path.join(utils.data_dir(), congress, "voteview")

        if congress in members_by_congress:
            utils.write_json(
                members_by_congress[congress],
                os.path.join(output_dir, "members.json")
            )

        if congress in parties_by_congress:
            utils.write_json(
                parties_by_congress[congress],
                os.path.join(output_dir, "parties.json")
            )

        logging.warn("Wrote voteview data for congress %s." % congress)


def floatornone(v):
    return float(v) if v and v.strip() else None


def intornone(v):
    return int(float(v)) if v and v.strip() else None


def parse_member(row):
    return {
        "bioguide_id": row["bioguide_id"] if row.get("bioguide_id", "").strip() else None,
        "icpsr": intornone(row.get("icpsr")),
        "congress": int(row["congress"]),
        "chamber": row["chamber"],
        "state": row["state_abbrev"] if row.get("state_abbrev", "").strip() else None,
        "district": intornone(row.get("district_code")),
        "party_code": intornone(row.get("party_code")),
        "name": row["bioname"] if row.get("bioname", "").strip() else None,
        "born": intornone(row.get("born")),
        "died": intornone(row.get("died")),
        "nominate": {
            "dim1": floatornone(row.get("nominate_dim1")),
            "dim2": floatornone(row.get("nominate_dim2")),
            "log_likelihood": floatornone(row.get("nominate_log_likelihood")),
            "geo_mean_probability": floatornone(row.get("nominate_geo_mean_probability")),
            "conditional": row["conditional"] == "1" if row.get("conditional", "").strip() else None,
        },
        "nokken_poole": {
            "dim1": floatornone(row.get("nokken_poole_dim1")),
            "dim2": floatornone(row.get("nokken_poole_dim2")),
        },
    }


def parse_party(row):
    return {
        "congress": int(row["congress"]),
        "chamber": row["chamber"],
        "party_code": intornone(row.get("party_code")),
        "party_name": row["party_name"] if row.get("party_name", "").strip() else None,
        "n_members": intornone(row.get("n_members")),
        "nominate": {
            "dim1_median": floatornone(row.get("nominate_dim1_median")),
            "dim2_median": floatornone(row.get("nominate_dim2_median")),
            "dim1_mean": floatornone(row.get("nominate_dim1_mean")),
            "dim2_mean": floatornone(row.get("nominate_dim2_mean")),
        },
    }
