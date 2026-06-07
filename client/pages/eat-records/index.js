const WXAPI = require('../../wxapi/main')
const CONFIG = require('../../config.js')
const {
  appendRecordsPage,
  removeRecordAfterDelete
} = require('../../utils/dinner-plan.js')

Page({
  data: {
    records: [],
    page: 1,
    pageSize: 20,
    loading: false,
    hasMore: true
  },
  onLoad: function() {
    this.loadRecords(true)
  },
  onShow: function() {
    this.loadRecords(true)
  },
  onPullDownRefresh: function() {
    this.loadRecords(true).finally(() => {
      wx.stopPullDownRefresh()
    })
  },
  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadRecords(false)
    }
  },
  loadRecords: function(reset) {
    const page = reset ? 1 : this.data.page + 1
    this.setData({ loading: true })
    return WXAPI.eatRecords({
      user_id: CONFIG.fixedUserId,
      page,
      page_size: this.data.pageSize
    }).then(res => {
      if (res.code !== 0) {
        wx.showToast({
          title: res.message || '加载失败',
          icon: 'none'
        })
        return
      }
      const records = res.data.records || []
      this.setData({
        records: appendRecordsPage(this.data.records, records, reset),
        page,
        hasMore: records.length >= this.data.pageSize
      })
    }).catch(() => {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }).finally(() => {
      this.setData({ loading: false })
    })
  },
  deleteRecord: function(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '要删除这条一起吃过记录吗？',
      success: res => {
        if (!res.confirm) {
          return
        }
        WXAPI.deleteEatRecord(id).then(result => {
          if (result.code === 0) {
            this.setData({
              records: removeRecordAfterDelete(this.data.records, id, true)
            })
            return
          }
          wx.showToast({
            title: result.message || '删除失败',
            icon: 'none'
          })
        }).catch(() => {
          wx.showToast({
            title: '删除失败',
            icon: 'none'
          })
        })
      }
    })
  }
})
