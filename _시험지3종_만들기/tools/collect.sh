# 완성된 학교 결과물을 repo로 복사: bash collect.sh <name>...
WS=${WS:-/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad}; R=/home/user/-/_시험지3종_만들기
mkdir -p "$R/적중리포트"
for n in "$@"; do
  o="$WS/school_out/$n"; [ -f "$o/${n}_적중리포트.pdf" ] || { echo "미완성 $n"; continue; }
  mkdir -p "$R/학교시험/$n"; cp "$o"/*\(*\).pdf "$R/학교시험/$n/"
  cp "$o/${n}_적중리포트.pdf" "$R/적중리포트/${n}_채수학_적중리포트.pdf"; echo "OK $n"
done
