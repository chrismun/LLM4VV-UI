#include <stdio.h>
#include <assert.h>

#define CHECK(x) do { if (!(x)) { printf("Check failed: %s\n", #x); return 1; } } while(0)
#define CHECK_EQUAL(x, y) CHECK((x) == (y))

void test_kernels(const char *desc, int expected, int num_gangs, int num_workers, int vector_length) {
    int i, j;
    int expected_match_count = 0;

    #pragma acc kernels num_gangs(num_gangs) num_workers(num_workers) vector_length(vector_length)
    {
        #pragma acc loop
        for (i = 0; i < 10; ++i) {
            #pragma acc loop
            for (j = 0; j < 10; ++j) {
                if (i == j) {
                    expected_match_count++;
                }
            }
        }
    }

    CHECK_EQUAL(expected_match_count, expected);
}

int main() {
    int passed = 0;

    // Test 1: kernels construct without any clauses (default values)
    test_kernels("Default num_gangs, num_workers, and vector_length", 10, 0, 0, 0);
    passed++;

    // Test 2: kernels construct with default num_gangs and num_workers, but explicit vector_length
    test_kernels("Default num_gangs and num_workers with explicit vector_length", 81, 0, 0, 16);
    passed++;

    // Test 3: kernels construct with num_gangs clause and default num_workers and vector_length
    test_kernels("Explicit num_gangs with default num_workers and vector_length", 55, 2, 0, 0);
    passed++;

    // Test 4: kernels construct with num_workers clause and default num_gangs and vector_length
    test_kernels("Explicit num_workers with default num_gangs and vector_length", 10, 0, 16, 0);
    passed++;

    // Test 5: kernels construct with nested kernels constructs (inner most takes precedence)
    {
        int i, j;
        int expected_match_count = 0;

        #pragma acc kernels num_gangs(2) num_workers(8) vector_length(4)
        {
            #pragma acc kernels num_gangs(4) num_workers(4) vector_length(2)
            {
                #pragma acc loop
                for (i = 0; i < 10; ++i) {
                    #pragma acc loop
                    for (j = 0; j < 10; ++j) {
                        if (i != j) {
                            expected_match_count++;
                        }
                    }
                }
            }
        }

        CHECK_EQUAL(expected_match_count, 45); // Half of the off-diagonal elements should not match
        passed++;
    }

    printf("Passed %d tests\n", passed);
    return passed == 5 ? 0 : 1; // Return 0 if all tests pass, 1 otherwise
}