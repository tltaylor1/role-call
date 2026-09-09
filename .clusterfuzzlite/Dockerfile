# The fuzzing build image, pinned by digest like every other base
# image here. ClusterFuzzLite builds the harnesses under fuzz/ against
# the same hash-pinned tree the application runs, so a crash it finds
# is a crash in the shipped parsers, not in a lookalike.
FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:ba1e90ca5105f863688fd5dd4a945b41cdaafe26b58b5df8ce10e2efb10dd809
COPY . $SRC/role-call
WORKDIR $SRC/role-call
COPY .clusterfuzzlite/build.sh $SRC/
