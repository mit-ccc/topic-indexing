#!/usr/bin/env python3

"""
A script that demonstrates how one might use the expanded
term lists produced by generate_topic_terms; for each snippet
in the input, output a list of probabilities P(topic | snippet)
for each topic, based on a naive keyword-containment model.

Example:
  ./add_topic_probabilities.py example_topics_output.json < dfAll.json
"""

from collections import defaultdict
import json
import re
import sys

def tokenize(s):
    return re.sub(r"[^0-9A-Za-z]", " ", s).split()

def snippets_to_topic_probabilities(snippet_list, term_to_topics):
    """Given a list of text snippets as strings, and a term->topics
    map, produce a list of probabilities P(topic | token) for each topic."""
    res = defaultdict(lambda: 0) # tag -> count
    num_tokens = 0
    for snippet in snippet_list:
        tokens = tokenize(snippet.lower())
        num_tokens += len(tokens)
        for i, token0 in enumerate(tokens):
            terms_to_check = [token0] + (
                (i < len(tokens) - 1) and [token0 + "_" + tokens[i+1]] or [])
            for t in terms_to_check:
                if t in term_to_topics:
                    for topic in term_to_topics[t]:
                        res[topic] += 1

    # Convert to probabilities
    if num_tokens:
        return dict([k, round(v / num_tokens, 6)] for k, v in res.items())
    return {}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <topic_map.json> < input_json" % (sys.argv[0]))
        sys.exit(1)
    term_to_topics = defaultdict(lambda: [])
    topics_doc = json.loads(open(sys.argv[1], "r").read())
    for topic, term_list in topics_doc["topics"].items():
        for term_obj in term_list:
            term_to_topics[term_obj["term"]].append(topic)
    conversation_doc = json.loads(sys.stdin.read())
    snippets = conversation_doc["snips"]
    output_probs = {}   # snip_id -> {topic_code -> prob}
    for k, v in snippets.items():
        topic_probs = snippets_to_topic_probabilities([v], term_to_topics)
        output_probs[k] = topic_probs
    conversation_doc["snippet_topic_probs"] = output_probs
    conversation_doc["overall_topic_probs"] = snippets_to_topic_probabilities(
        snippets.values(), term_to_topics)
    print(json.dumps(conversation_doc))
