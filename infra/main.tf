resource "aws_s3_bucket" "test-wf-12345" {
  bucket        = "test-wf-12345"
  force_destroy = true
  tags = {
    env  = "test-wf"
    name = "test-wf-12345"
  }
}
