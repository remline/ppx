#!/bin/bash
echo -----punc stdout-----
diff test/expect/punc-stdout <(./punc < test/punc 2>/dev/null)
echo -----punc stderr-----
diff test/expect/punc-stderr <(./punc < test/punc 2>&1 1>/dev/null)
echo -----punc-error stderr-----
diff test/expect/punc-error-stderr <(./punc < test/punc-error 2>&1 1>/dev/null)
