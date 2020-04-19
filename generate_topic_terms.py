#!/usr/bin/env python3

"""
This tool generates an expanded set of "topic terms" from a configuration
file (--topic_yaml_file) by cross-referencing the terms in a word2vec
model (--word2vec_model).  For more clarity on what that means and an example
config, see ./topics.yml
"""

import argparse
import json
import logging

from gensim.models import Word2Vec
from yaml import load as yaml_load

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics_yaml_file",
                        help="path to config file for topics",
                        default="./topics.yml")
    parser.add_argument("--word2vec_model",
                        help="path to word2vec_model for determing terms",
                        default="./models/radiotalk_2020-04_w2v")
    parser.add_argument("--enforce_disjoint_terms", default=False,
                        action="store_true",
                        help="if set, allow a term to appear in at most one topic")
    args = parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)

    tag_config = yaml_load(open(args.topics_yaml_file).read())
    logging.debug("Loaded topic config; %d topics defined", len(tag_config["topics"]))
    logging.debug("Loading word2vec model from %s", args.word2vec_model)
    model = Word2Vec.load(args.word2vec_model)
    model_vocab = model.wv.vocab

    logging.debug("Generating expanded topic terms.")
    lines = []
    for x in tag_config["topics"]:
        if "values_file" in x:
            values = open(x["values_file"]).read().split("\n")
        else:
            values = x["values"]
        matches = set()
        match_strengths = {}

        # for softmatch_min_similarity_mean
        term_sums = {}
        term_counts = {}
        num_additions = 0

        if "softmatch_min_similarity_any" in x:
            min_similarity = x["softmatch_min_similarity_any"]
        else:
            min_similarity = 0

        if "softmatch_min_similarity_mean" in x:
            min_mean_similarity = x["softmatch_min_similarity_mean"]
        else:
            min_mean_similarity = 0

        terms = [val.lower().replace(" ", "_") for val in values]
        for term in terms:
            matches.add(term)
            match_strengths[term] = 1.0

            # If one of these are specified, we need to get the semantic
            # neighbors
            if not (min_similarity or min_mean_similarity) or term not in model_vocab:
                continue

            similarities = model.most_similar(positive=term, topn=200000)
            for similar_term, sim in similarities:
                if min_similarity and similar_term not in matches:
                    if sim < min_similarity:
                        break
                    logging.debug("For tag '%s': Adding similar term '%s' " +
                                  "(similar to '%s' with similarity %f)",
                                  x["id"], similar_term, term, sim)
                    if not min_mean_similarity and ("max_to_add" not in x
                                                    or num_additions < x["max_to_add"]):
                        matches.add(similar_term)
                        match_strengths[similar_term] = sim
                        num_additions += 1
                if min_mean_similarity:
                    term_sums[similar_term] = term_sums.get(similar_term, 0) + sim * sim
                    term_counts[similar_term] = term_counts.get(similar_term, 0) + 1

        if min_mean_similarity:
            # Determine the terms above the mean, take the top max_to_add of them
            # (if specified)
            new_addition_candidates = []
            for similar_term, term_sum in term_sums.items():
                mean_similarity = term_sums[similar_term] / term_counts[similar_term]
                if mean_similarity >= min_mean_similarity:
                    new_addition_candidates.append((similar_term, mean_similarity))
            # Sort descending by similarity
            new_addition_candidates.sort(key=lambda x: x[1], reverse=True)
            for similar_term, mean_similarity in new_addition_candidates:
                if "max_to_add" in x and num_additions >= x["max_to_add"]:
                    break
                if similar_term not in matches:
                    matches.add(similar_term)
                    match_strengths[similar_term] = mean_similarity
                    num_additions += 1
                    logging.debug("For tag '%s':  Adding %s %f",
                                  x["id"], similar_term, mean_similarity)

        # Cluster to group near-synonyms together
        term_classes = {}
        for m in matches:
            if m in model_vocab:
                similarities = model.most_similar(positive=m, topn=100)
            else:
                similarities = []
            term_class = m
            for similar_term, sim in similarities:
                if sim > 0.75 and similar_term in term_classes:
                    term_class = term_classes[similar_term]
            term_classes[m] = term_class
            strength = match_strengths[m]
            lines.append((x["id"], m, term_class, strength))

    lines.sort(key=lambda x: x[3], reverse=True)
    seen_terms = set()
    output_obj = {}
    for topic, term, term_class, strength in lines:
        if args.enforce_disjoint_terms:
            if term in seen_terms:
                continue
            seen_terms.add(term)
        if topic not in output_obj:
            output_obj[topic] = []
        output_obj[topic].append({"term": term,
                                  "canonicalized_term": term_class,
                                  "strength": strength})
    print(json.dumps({"topics": output_obj}, indent=4))
