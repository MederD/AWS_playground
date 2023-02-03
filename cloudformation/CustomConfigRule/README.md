#### Template based on article from <https://aws.amazon.com/blogs/security/continuously-monitor-unused-iam-roles-aws-config/> with some extensions

#### Commands to run  

```text
aws cloudformation package --profile <Profile-Name> --region <Region> --template-file iam-role-last-used.yml --s3-bucket <S3-Bucket> --output-template-file iam-role-last-used-transformed.yml
```

```text
aws cloudformation deploy --profile <Profile-Name> --region <Region> --template-file iam-role-last-used-transformed.yml --stack-name <Stack-Name> --parameter-overrides file://./params.json --capabilities CAPABILITY_NAMED_IAM --notification-arns <Notification-Arn> --tags $(jq -r '.[] | [.ParameterKey, .ParameterValue] | "\(.[0])=\(.[1])"' stack-tags.json)
```
