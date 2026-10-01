export default function SafetyBanner() {
  return (<div className="bg-blue-50 dark:bg-blue-950 border border-blue-100 dark:border-blue-900 rounded-xl p-6">
      <h3 className="font-bold text-blue-900 mb-2">🛡️ Spotting Fake Job Offers</h3>
      <p className="text-sm text-blue-800">
        Legitimate employers never demand upfront payment via personal mobile money
        (M-Pesa, MTN MoMo, Orange Money) for training, verification, or processing fees.
        If a job asks you to pay before you're hired — it's likely a scam.
      </p>
    </div>
  )
}