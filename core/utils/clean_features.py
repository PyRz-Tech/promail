def clean_features(features_list, min_length=5):
	if not features_list:
		return []



	seen=set()
	unique_features = []


	for feature in features_list:
		feature_clean=feature.strip()
		if feature_clean.lower() not in seen:
			unique_features.append(feature_clean)
			seen.add(feature_clean.lower())


	filtered_features=[feature for feature in unique_features if len(feature) >= min_length]


	return filtered_features
