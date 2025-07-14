const axios = require('axios');

exports.handler = async (event) => {
  const webhookUrl = process.env.SLACK_WEBHOOK_URL;

  try {
    for (const record of event.Records) {
      const sns = record.Sns;

      let alarmDescription = sns.Message;

      try {
        const parsed = JSON.parse(sns.Message);
        if (parsed.AlarmDescription) {
          alarmDescription = parsed.AlarmDescription;
        }
      } catch (parseError) {
        console.warn("Message was not JSON. Using raw body.");
      }

      await axios.post(webhookUrl, {
        text: `🚨 *CloudWatch Alarm*\nSubject: ${sns.Subject}\nMessage: ${alarmDescription}`
      });
    }

    console.log("Notification sent successfully to Slack");
  } catch (error) {
    console.error("Failed to send notification to Slack", error);
    throw error;
  }
};
