Page({
  data: {
    nickName: "一起吃饭叭",
    avatarUrl: "/images/kefu.png"
  },
  goEatRecords: function() {
    wx.navigateTo({
      url: "/pages/eat-records/index"
    })
  },
  goDinnerPlan: function() {
    wx.navigateTo({ url: "/pages/dinner-plan/index" })
  },
  goPartner: function() {
    wx.navigateTo({ url: "/pages/partner/index" })
  },
  goFeedingValues: function() {
    wx.navigateTo({ url: '/pages/feeding-value/index' })
  },
  comingSoon: function() {
    wx.showToast({
      title: "后续开放",
      icon: "none"
    })
  },
  about: function() {
    wx.showModal({
      title: "关于我们",
      content: "一起吃饭叭，记录日常里认真吃过的每一顿。",
      showCancel: false
    })
  }
})
